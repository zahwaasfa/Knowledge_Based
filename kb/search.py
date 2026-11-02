"""Lapisan kueri graf (Neo4j) untuk skema terpadu: dokumen, chunk per-bagian, full-text fuzzy, vektor, ekspansi 1-2 hop."""
from __future__ import annotations
import difflib
import logging
import re
import time
from .config import S
from .db import DB
from .query_plan import analyze, fold, stem, terms

log = logging.getLogger("kb.search")
MONTH_NUMBERS = {name: number for number, names in enumerate((
    ("januari",), ("februari",), ("maret",), ("april",), ("mei",), ("juni",),
    ("juli",), ("agustus",), ("september",), ("oktober",), ("november",), ("desember",)
), 1) for name in names}


def _query_date_key(question: str) -> str | None:
    match = re.search(r"\b(\d{1,2})\s+([a-z]+)\s+((?:19|20)\d{2})\b", fold(question))
    if match and match.group(2) in MONTH_NUMBERS:
        day, month, year = int(match.group(1)), MONTH_NUMBERS[match.group(2)], match.group(3)
        return f"{year}{month:02d}{day:02d}"
    match = re.search(r"\b((?:19|20)\d{2})[-/](\d{1,2})[-/](\d{1,2})\b", question)
    if match:
        year, month, day = match.groups()
        return f"{year}{int(month):02d}{int(day):02d}"
    return None


FT_INDEXES = {
    "chunk": ["chunk_text_idn", "chunk_text_ft"],
    "document": ["document_idn", "document_ft"],
    "question": ["question_text_idn", "question_text_ft"],
    "answer": ["answer_text_idn"],
    "tag": ["tag_idn"],
    "reference": ["reference_idn"],
    "organization": ["organization_ft"],
}
_dead: set[str] = set()


def lucene(ts: list[str], fuzzy: bool = True, field: str | None = None, max_terms: int = 12) -> str:
    parts = []
    for t in ts[:max_terms]:
        t = re.sub(r"[^a-z0-9]", "", t)
        if not t:
            continue
        alts = [f"{t}^2"]
        if fuzzy and len(t) >= 5:
            alts.append(f"{t}~{2 if len(t) >= 9 else 1}")
        st = stem(t)
        if fuzzy and len(st) >= 4:
            alts.append(f"{st}*")
        parts.append("(" + " OR ".join(alts) + ")")
    q = " OR ".join(parts)
    return f"{field}:({q})" if field and q else q


def _safe(fn, default=None):
    try:
        return fn()
    except Exception as e:
        log.warning("query graf gagal: %s", str(e)[:200])
        return default if default is not None else []


def _ft(db: DB, kind: str, cypher_after_call: str, q: str, **params) -> list[dict]:
    if not q:
        return []
    for idx in FT_INDEXES[kind]:
        if idx in _dead:
            continue
        try:
            return db.read(f"CALL db.index.fulltext.queryNodes($index, $q) YIELD node, score\n{cypher_after_call}", index=idx, q=q, **params)
        except Exception as e:
            msg = str(e)
            if "index" in msg.lower() and ("not found" in msg.lower() or "no such" in msg.lower() or "does not exist" in msg.lower()):
                _dead.add(idx)
                continue
            return []
    return []


DOC_COLS = """d.doc_id AS doc_id, d.title AS title, d.year AS year, d.description AS description, d.benefit AS benefit,
       d.document_url AS url, d.file_name AS file_name, coalesce(d.has_physical_file,false) AS has_file, d.category AS category,
       d.subcategory AS subcategory, d.output_type AS output_type, d.knowledge_type AS knowledge_type, d.access_rights AS access_rights,
       toString(d.publish_date) AS publish_date, coalesce(d.tags_text,'') AS tags_text, coalesce(d.corpus,d.domain,'bappenas') AS corpus"""

DOC_FT = f"WITH node AS d, score WHERE $corpus IS NULL OR coalesce(d.corpus,d.domain,'bappenas')=$corpus WITH d, score ORDER BY score DESC LIMIT $limit RETURN {DOC_COLS}, score"
DOC_CATALOG = f"MATCH (d:Document) WHERE $corpus IS NULL OR coalesce(d.corpus,d.domain,'bappenas')=$corpus RETURN {DOC_COLS} LIMIT $limit"
DOC_BY_IDS = f"MATCH (d:Document) WHERE d.doc_id IN $ids AND ($corpus IS NULL OR coalesce(d.corpus,d.domain,'bappenas')=$corpus) RETURN {DOC_COLS}"
DOC_LEXICAL = f"""
MATCH (d:Document)
WHERE $corpus IS NULL OR coalesce(d.corpus,d.domain,'bappenas')=$corpus
WITH d, [t IN $terms WHERE toLower(d.title) CONTAINS t] AS ht,
        [t IN $terms WHERE toLower(coalesce(d.tags_text,'') + ' ' + coalesce(d.subcategory,'') + ' ' + coalesce(d.description,'')) CONTAINS t] AS ho
WHERE size(ht) > 0 OR size(ho) > 0
RETURN {DOC_COLS}, toFloat(size(ht) * 2 + size(ho)) AS score ORDER BY score DESC LIMIT $limit"""

_catalog: dict = {}


def doc_catalog(db: DB, corpus: str | None = None, ttl: int = 600) -> list[dict]:
    cached = _catalog.get(corpus)
    if not cached or time.time() - cached["t"] > ttl or not cached["rows"]:
        _catalog[corpus] = {"t": time.time(), "rows": _safe(lambda: db.read(DOC_CATALOG, limit=5000, corpus=corpus))}
    return _catalog[corpus]["rows"]


def docs_by_ids(db: DB, ids: list[str], corpus: str | None = None) -> list[dict]:
    rows = _safe(lambda: db.read(DOC_BY_IDS, ids=ids, corpus=corpus)) if ids else []
    order = {i: n for n, i in enumerate(ids)}
    return sorted(rows, key=lambda r: order.get(r["doc_id"], 99))


def _tok_match(qs: set[str], ts: set[str], fuzzy_cut: float = 0.84) -> float:
    hit = 0.0
    for q in qs:
        if q in ts:
            hit += 1
        else:
            best = max((difflib.SequenceMatcher(None, q, t).ratio() for t in ts if abs(len(t) - len(q)) <= 3), default=0)
            if len(q) >= 5 and best >= fuzzy_cut:
                hit += 0.8
    return hit


def rank_documents(plan, rows: list[dict]) -> list[dict]:
    q = plan.topic_stems
    qn = {t for t in q if not t.isdigit()}
    mx = max((r.get("score") or 0 for r in rows), default=0) or 1.0
    wanted_date = _query_date_key(plan.raw)
    out = []
    for r in rows:
        tt = {stem(t) for t in terms(r["title"])}
        ft = {stem(t) for t in terms(r.get("file_name") or "")}
        other = {stem(t) for t in terms(f'{r.get("tags_text","")} {r.get("subcategory") or ""} {(r.get("description") or "")[:400]}')}
        cov = _tok_match(qn, tt) / len(qn) if qn else 0.0
        file_cov = _tok_match(qn, ft) / len(qn) if qn else 0.0
        cov2 = _tok_match(qn - tt, other) / len(qn) if qn else 0.0
        prec = len(qn & tt) / max(len(tt), 1)
        date_match = bool(wanted_date and wanted_date in re.sub(r"\D", "", str(r.get("file_name") or "")))
        s = 0.54 * cov + 0.12 * file_cov + 0.10 * cov2 + 0.12 * prec + 0.06 * ((r.get("score") or 0) / mx)
        if wanted_date:
            s += 0.14 if date_match else -0.08
        if plan.year:
            s += 0.06 if plan.year in tt or str(r.get("year")) == plan.year else -0.06
        out.append({**r, "cover": round(max(cov, file_cov), 3), "date_match": date_match, "rank": round(s, 4)})
    return sorted(out, key=lambda x: x["rank"], reverse=True)


def find_documents(db: DB, plan, limit: int = 8, corpus: str | None = None) -> tuple[list[dict], list[str]]:
    stages, rows = [], {}
    ts = [t for t in plan.topic if t]
    if not ts:
        return [], stages
    q = lucene(ts, field="title") + " OR " + lucene(ts)
    for r in _ft(db, "document", DOC_FT, q, limit=30, corpus=corpus):
        rows[r["doc_id"]] = r
    if rows:
        stages.append("document_ft(fuzzy)")
    if len(rows) < 3:
        for r in _safe(lambda: db.read(DOC_LEXICAL, terms=ts, limit=30, corpus=corpus)):
            rows.setdefault(r["doc_id"], r)
        stages.append("document_contains")
    cat = doc_catalog(db, corpus)
    if cat:
        qn = {stem(t) for t in ts if not t.isdigit()}
        for r in cat:
            if r["doc_id"] in rows:
                continue
            tt = {stem(t) for t in terms(r["title"])}
            ft = {stem(t) for t in terms(r.get("file_name") or "")}
            date_match = bool(_query_date_key(plan.raw) and _query_date_key(plan.raw) in re.sub(r"\D", "", str(r.get("file_name") or "")))
            if qn and (max(_tok_match(qn, tt), _tok_match(qn, ft)) / len(qn) >= 0.35 or date_match):
                rows[r["doc_id"]] = {**r, "score": 0.0}
        stages.append("katalog_typo")
    return rank_documents(plan, list(rows.values()))[:limit], stages


CHUNK_COLS = """c.chunk_id AS chunk_id, c.doc_id AS doc_id, c.section AS section, c.item_no AS item_no, c.text AS text, c.level AS level,
       c.is_leaf AS is_leaf, c.breadcrumb AS breadcrumb, c.page_number AS page, c.chunk_index AS chunk_index,
       d.title AS title, d.document_url AS url, d.file_name AS file_name"""

SECTION_CHUNKS = f"""
MATCH (c:Chunk) WHERE c.doc_id IN $ids AND c.section IN $sections
MATCH (d:Document {{doc_id:c.doc_id}})
RETURN {CHUNK_COLS}
ORDER BY c.doc_id, c.section, coalesce(c.item_no, 0), c.chunk_index"""

BODY_CHUNKS = f"""
MATCH (c:Chunk) WHERE c.doc_id IN $ids AND c.section IS NULL AND c.breadcrumb CONTAINS 'Isi Dokumen' AND c.level <= $maxlevel
MATCH (d:Document {{doc_id:c.doc_id}})
RETURN {CHUNK_COLS}
ORDER BY c.doc_id, c.level, c.chunk_index LIMIT $limit"""

CHUNK_FT = f"""
WITH node AS c, score
MATCH (d:Document {{doc_id:c.doc_id}})
WHERE $corpus IS NULL OR coalesce(d.corpus,d.domain,'bappenas')=$corpus
WITH c, d, score ORDER BY score DESC LIMIT $limit
RETURN {CHUNK_COLS}, score"""

CHUNK_VEC = f"""
CALL db.index.vector.queryNodes('chunk_embedding', $candidate_limit, $vec) YIELD node AS c, score
MATCH (d:Document {{doc_id:c.doc_id}})
WHERE $corpus IS NULL OR coalesce(d.corpus,d.domain,'bappenas')=$corpus
WITH c, d, score ORDER BY score DESC LIMIT $limit
RETURN {CHUNK_COLS}, score"""

CHUNK_LEXICAL = f"""
MATCH (c:Chunk) WHERE c.doc_id IN $ids
WITH c, [t IN $terms WHERE toLower(c.text) CONTAINS t] AS hit WHERE size(hit) > 0
MATCH (d:Document {{doc_id:c.doc_id}})
WHERE $corpus IS NULL OR coalesce(d.corpus,d.domain,'bappenas')=$corpus
RETURN {CHUNK_COLS}, toFloat(size(hit)) AS score ORDER BY score DESC LIMIT $limit"""

GRAPH_GROUNDED_CHUNKS = f"""
MATCH (node)
WHERE (node:Tag OR node:Organization OR node:Reference OR node:Category OR node:SubCategory)
  AND any(t IN $terms WHERE toLower(coalesce(node.name, node.title, '')) CONTAINS t)
MATCH (node)-[:MENTIONED_IN|TAGGED_WITH|BELONGS_TO_ORG|IN_CATEGORY]-(c:Chunk)
MATCH (d:Document {{doc_id:c.doc_id}})
WHERE $corpus IS NULL OR coalesce(d.corpus,d.domain,'bappenas')=$corpus
RETURN {CHUNK_COLS}, labels(node)[0] AS entity_kind, coalesce(node.name, node.title) AS entity_name
LIMIT $limit
"""


def section_chunks(db: DB, doc_ids: list[str], sections: list[str]) -> list[dict]:
    return _safe(lambda: db.read(SECTION_CHUNKS, ids=doc_ids, sections=sections)) if doc_ids and sections else []


def body_chunks(db: DB, doc_ids: list[str], maxlevel: int = 2, limit: int = 8) -> list[dict]:
    return _safe(lambda: db.read(BODY_CHUNKS, ids=doc_ids, maxlevel=maxlevel, limit=limit)) if doc_ids else []


NEIGHBOR_CHUNKS = """
MATCH (c:Chunk) WHERE c.chunk_id IN $ids
MATCH (c)-[:SUB_CHUNK_OF]->(p:Chunk)
MATCH (s:Chunk)-[:SUB_CHUNK_OF]->(p)
WHERE s.chunk_id <> c.chunk_id AND s.chunk_index IS NOT NULL AND c.chunk_index IS NOT NULL
  AND abs(s.chunk_index - c.chunk_index) <= $window
RETURN c.chunk_id AS chunk_id, c.chunk_index AS idx, s.chunk_id AS nb_id, s.chunk_index AS nb_idx, s.text AS text
"""


def neighbor_chunks(db: DB, chunk_ids: list[str], window: int = 1) -> dict[str, list[dict]]:
    """Traversal graf SUB_CHUNK_OF: saudara berurutan (percakapan sebelum/sesudah) dari chunk daun terpilih.
    Chunk transkrip hanya satu giliran bicara, sehingga tetangga memberi konteks yang diperlukan untuk menjawab."""
    if not chunk_ids or window < 1:
        return {}
    rows = _safe(lambda: db.read(NEIGHBOR_CHUNKS, ids=list(chunk_ids), window=int(window)))
    out: dict[str, list[dict]] = {}
    for r in sorted(rows, key=lambda r: (r["chunk_id"], r["nb_idx"])):
        out.setdefault(r["chunk_id"], []).append({
            "chunk_id": r["nb_id"], "text": r.get("text") or "", "position": "before" if r["nb_idx"] < r["idx"] else "after"})
    return out


def rrf(lists: list[list[dict]], key: str = "chunk_id", k: int = 60,
        methods: list[str] | None = None, weights: list[float] | None = None) -> list[dict]:
    acc: dict = {}
    for list_index, lst in enumerate(lists):
        method = methods[list_index] if methods and list_index < len(methods) else "unknown"
        for rank, r in enumerate(lst):
            e = acc.setdefault(r[key], {**r, "rrf": 0.0, "retrieval_methods": [], "retrieval_ranks": {}})
            w = weights[list_index] if weights and list_index < len(weights) else 1.0
            e["rrf"] += w / (k + rank + 1)
            for inherited in r.get("retrieval_methods", []):
                if inherited not in e["retrieval_methods"]:
                    e["retrieval_methods"].append(inherited)
            if method not in e["retrieval_methods"]:
                e["retrieval_methods"].append(method)
            e["retrieval_ranks"].update(r.get("retrieval_ranks", {}))
            for path in r.get("graph_paths", []):
                if path not in e.setdefault("graph_paths", []):
                    e["graph_paths"].append(path)
            e["retrieval_ranks"][method] = rank + 1
            e.setdefault("retrieval_scores", {}).update(r.get("retrieval_scores", {}))
            e["retrieval_scores"][method] = r.get("score")
    return sorted(acc.values(), key=lambda x: x["rrf"], reverse=True)


def _graph_chunk_hits(db: DB, plan, top_k: int, corpus: str | None) -> list[dict]:
    """Penelusuran Graph RAG yang secara langsung menarik TEKS CHUNK ter-grounding."""
    ts = [t for t in plan.topic if not t.isdigit()] or plan.topic
    if not ts:
        return []
    
    # 1. Tarik Chunk ter-grounding langsung dari entitas graph
    grounded = _safe(lambda: db.read(GRAPH_GROUNDED_CHUNKS, terms=[t.lower() for t in ts], limit=top_k * 4, corpus=corpus))
    
    # 2. Tarik dokumen/entitas tetangga untuk jalur graph metadata
    entities = entity_docs(db, plan, limit=max(top_k * 2, 8), corpus=corpus)
    seed_ids = list(dict.fromkeys(row["doc_id"] for row in entities))[:max(top_k, 5)]
    
    path_by_doc: dict[str, list[dict]] = {}
    for row in entities:
        path = {"hops": 0, "entity_kind": row.get("kind"), "entity": row.get("entity"),
                "relationship": row.get("rel"), "role": row.get("role")}
        if path not in path_by_doc.setdefault(row["doc_id"], []):
            path_by_doc[row["doc_id"]].append(path)
            
    neighbors = expand_graph(db, seed_ids, limit=max(top_k, 5), two_hop=False, corpus=corpus) if seed_ids else []
    doc_ids = list(dict.fromkeys(seed_ids + [row["doc_id"] for row in neighbors]))[:max(top_k * 2, 8)]
    for row in neighbors:
        path = {"hops": row.get("hops"), "via": row.get("via"), "shared": row.get("shared", [])}
        if path not in path_by_doc.setdefault(row["doc_id"], []):
            path_by_doc[row["doc_id"]].append(path)

    lex_rows = _safe(lambda: db.read(CHUNK_LEXICAL, ids=doc_ids, terms=ts, limit=top_k * 4, corpus=corpus)) if doc_ids else []
    
    # Gabungkan grounded chunks dan lexical doc chunks
    combined = {r["chunk_id"]: r for r in (grounded + lex_rows)}
    rows = list(combined.values())
    
    for row in rows:
        row.setdefault("score", 1.0)
        row["graph_paths"] = path_by_doc.get(row["doc_id"], [])
        row["retrieval_methods"] = ["graph_entity_document_chunks"]
    return rows


def rerank_vector_hits(question: str, hits: list[dict]) -> list[dict]:
    unique = {}
    for hit in hits:
        unique.setdefault(hit.get("chunk_id"), hit)
    hits = list(unique.values())
    qterms = {stem(t) for t in analyze(question).topic if not t.isdigit()}
    wanted_date = _query_date_key(question)
    if not hits or not qterms:
        return hits
    scored = []
    for rank, hit in enumerate(hits):
        content = {stem(t) for t in terms(str(hit.get("text") or ""))}
        metadata = {stem(t) for t in terms(" ".join(str(hit.get(k) or "") for k in ("title", "file_name", "breadcrumb", "section")))}
        coverage = _tok_match(qterms, content | metadata) / len(qterms)
        title_coverage = _tok_match(qterms, metadata) / len(qterms)
        rank_prior = 1.0 - rank / max(len(hits), 1)
        date_match = bool(wanted_date and wanted_date in re.sub(r"\D", "", str(hit.get("file_name") or "")))
        hit["vector_rank"] = rank + 1
        hit["query_coverage"] = round(coverage, 4)
        hit["metadata_coverage"] = round(title_coverage, 4)
        hit["date_match"] = date_match
        date_weight = 0.12 if wanted_date and date_match else (-0.05 if wanted_date else 0.0)
        hit["rerank_score"] = round(0.3 * rank_prior + 0.48 * coverage + 0.1 * title_coverage + date_weight, 6)
        scored.append(hit)
    return sorted(scored, key=lambda hit: hit["rerank_score"], reverse=True)


def search_chunks(db: DB, plan, top_k: int = 6, doc_ids: list[str] | None = None,
                  corpus: str | None = None, restrict_doc_ids: bool = False,
                  use_vector: bool | None = None) -> tuple[list[dict], list[str]]:
    """Retrieval Graph RAG. Vector tidak dicampur secara default (GRAPH_RAG_USE_VECTOR=false) agar
    konteks Graph RAG dan Vector RAG tetap terpisah dan dapat dibandingkan secara adil."""
    stages, lists, methods = [], [], []
    if use_vector is None:
        use_vector = S.graph_use_vector
    ts = [t for t in plan.topic if not t.isdigit()] or plan.topic
    q = lucene(ts)
    ft = _ft(db, "chunk", CHUNK_FT, q, limit=max(top_k * 8, 40), corpus=corpus)
    if ft:
        lists.append(ft); methods.append("fulltext"); stages.append("chunk_ft(fuzzy)")
    if S.embeddings and use_vector:
        from .embeddings import embed
        v = embed([plan.raw])
        if v:
            vec = _safe(lambda: db.read(CHUNK_VEC, vec=v[0], limit=max(top_k * 4, 20), candidate_limit=max(top_k * 20, 100), corpus=corpus))
            if vec:
                lists.append(vec); methods.append("vector"); stages.append("chunk_vector")
    graph = _graph_chunk_hits(db, plan, top_k, corpus)
    if graph:
        lists.append(graph); methods.append("graph_entity_document_chunks"); stages.append("graph_entity_document_chunks")
    weights = [S.graph_entity_weight if m == "graph_entity_document_chunks" else 1.0 for m in methods]
    fused = rrf(lists, methods=methods, weights=weights) if lists else []
    stages.append(f"fused_candidates={len(fused)}")
    if restrict_doc_ids and doc_ids:
        keep = set(doc_ids)
        filtered = [row for row in fused if row["doc_id"] in keep]
        if filtered:
            fused = filtered
            stages.append(f"scoped_to_resolved_docs={len(filtered)}")
    if doc_ids and len(fused) < top_k:
        lex = _safe(lambda: db.read(CHUNK_LEXICAL, ids=doc_ids, terms=ts, limit=top_k * 4, corpus=corpus))
        if lex:
            if fused:
                fused = rrf([fused, lex], methods=["hybrid", "document_lexical"])
            else:
                fused = rrf([lex], methods=["document_lexical"])
            stages.append("chunk_lexical(doc)")
    qn = {stem(t) for t in ts if not t.isdigit()}
    if qn:
        for r in fused:
            toks = {stem(t) for t in terms(f'{r.get("breadcrumb") or ""} {r["text"]}')}
            r["cov"] = _tok_match(qn, toks) / len(qn)
    best, stages_sel = select_top(fused, top_k)
    return best, stages + stages_sel


def _norm_text(t: str) -> str:
    return " ".join(fold(t or "").split())


def select_top(fused: list[dict], top_k: int, per_doc_cap: int | None = None,
               min_cov_graph_only: float | None = None) -> tuple[list[dict], list[str]]:
    """Skor akhir + deduplikasi + pemilihan top_k.

    Perbaikan dari audit: (1) batas `per_doc >= 3` lama menghentikan seleksi di ~3 chunk walau ~60 kandidat tersedia
    (korpus notetaker = 1 dokumen per pertanyaan) -> kini dua-lintasan: lintasan 1 menjaga keragaman dokumen
    (cap per dokumen), lintasan 2 mengisi sisa slot dari kandidat berperingkat berikutnya, sehingga top_k terisi;
    (2) kandidat yang HANYA berasal dari jalur entitas graf dan tidak memuat istilah pertanyaan dibuang;
    (3) chunk berteks identik dibuang (duplikasi parent-child / teks sama).
    """
    per_doc_cap = S.graph_per_doc_cap if per_doc_cap is None else per_doc_cap
    min_cov = S.graph_min_cov if min_cov_graph_only is None else min_cov_graph_only
    stages: list[str] = []
    max_rrf = max((r.get("rrf", 0.0) for r in fused), default=1.0) or 1.0
    for r in fused:
        r["rrf_normalized"] = r.get("rrf", 0.0) / max_rrf
        r["rank"] = 0.75 * r["rrf_normalized"] + 0.25 * r.get("cov", 0.0)
        if r.get("section") == "identitas":
            r["rank"] *= 0.85
    fused = sorted(fused, key=lambda x: x["rank"], reverse=True)
    dropped_cov = 0
    pool = []
    for r in fused:
        only_entity = r.get("retrieval_methods") == ["graph_entity_document_chunks"]
        if only_entity and "cov" in r and r["cov"] < min_cov:
            dropped_cov += 1
            continue
        pool.append(r)
    if not pool:           # jangan kosongkan hasil bila filter terlalu ketat
        pool, dropped_cov = fused, 0
    if dropped_cov:
        stages.append(f"drop_graph_only_low_coverage={dropped_cov}")
    seen_txt: set[str] = set()
    uniq = []
    for r in pool:
        key = _norm_text(r.get("text"))
        if key in seen_txt:
            continue
        seen_txt.add(key)
        uniq.append(r)
    if len(uniq) < len(pool):
        stages.append(f"dedup_text={len(pool) - len(uniq)}")
    best, per_doc, chosen = [], {}, set()
    for r in uniq:                                   # lintasan 1: keragaman dokumen
        if per_doc.get(r["doc_id"], 0) >= per_doc_cap:
            continue
        per_doc[r["doc_id"]] = per_doc.get(r["doc_id"], 0) + 1
        best.append(r); chosen.add(r["chunk_id"])
        if len(best) >= top_k:
            break
    if len(best) < top_k:                            # lintasan 2: isi sisa slot berdasarkan peringkat
        for r in uniq:
            if r["chunk_id"] in chosen:
                continue
            best.append(r); chosen.add(r["chunk_id"])
            if len(best) >= top_k:
                break
        stages.append("backfill_to_top_k")
    best.sort(key=lambda x: x["rank"], reverse=True)
    return best, stages


def vector_only_chunks(db: DB, question: str, top_k: int = 5, corpus: str | None = None,
                       doc_id: str | None = None) -> list[dict]:
    if not S.embeddings:
        raise RuntimeError("Vector RAG memerlukan EMBEDDINGS=true dan ingest ulang agar embedding chunk dibuat.")
    from .embeddings import embed

    vectors = embed([question])
    if not vectors:
        raise RuntimeError("Embedding pertanyaan gagal dibuat; periksa konfigurasi model embedding.")
    counts = db.read("""
        MATCH (c:Chunk) WHERE c.embedding IS NOT NULL
        RETURN count(c) AS total,
               sum(CASE WHEN ($corpus IS NULL OR coalesce(c.corpus,'bappenas')=$corpus)
                         AND ($doc_id IS NULL OR c.doc_id=$doc_id) THEN 1 ELSE 0 END) AS scoped
    """, corpus=corpus, doc_id=doc_id)
    total = counts[0]["total"] if counts else 0
    scoped = counts[0]["scoped"] if counts else 0
    if not scoped:
        doc_id = None
        total = db.read("MATCH (c:Chunk) WHERE c.embedding IS NOT NULL RETURN count(c) AS total")[0]["total"]

    hits = db.read(f"""
        CALL db.index.vector.queryNodes('chunk_embedding', $candidate_limit, $vec) YIELD node AS c, score
        MATCH (d:Document {{doc_id:c.doc_id}})
        WHERE ($corpus IS NULL OR coalesce(c.corpus,d.corpus,d.domain,'bappenas')=$corpus)
          AND ($doc_id IS NULL OR c.doc_id=$doc_id)
        RETURN {CHUNK_COLS}, score
        ORDER BY score DESC LIMIT $top_k
    """, candidate_limit=total, vec=vectors[0], corpus=corpus, doc_id=doc_id, top_k=top_k)

    if not hits and doc_id:
        hits = db.read(f"""
            CALL db.index.vector.queryNodes('chunk_embedding', $candidate_limit, $vec) YIELD node AS c, score
            MATCH (d:Document {{doc_id:c.doc_id}})
            WHERE ($corpus IS NULL OR coalesce(c.corpus,d.corpus,d.domain,'bappenas')=$corpus)
            RETURN {CHUNK_COLS}, score
            ORDER BY score DESC LIMIT $top_k
        """, candidate_limit=total, vec=vectors[0], corpus=corpus, doc_id=None, top_k=top_k)
    return hits


def similar_questions(db: DB, plan, limit: int = 6, corpus: str | None = None) -> list[dict]:
    return _ft(db, "question", "WITH node AS q, score MATCH (q)-[:ANSWERED_BY]->(a:Answer) RETURN q.question_id AS question_id, q.text AS question, a.text AS answer, score", lucene(plan.topic), limit=limit, corpus=corpus)


def answer_sources(db: DB, qid: str, limit: int = 8, corpus: str | None = None) -> list[dict]:
    return _safe(lambda: db.read("MATCH (q:Question {question_id:$qid})-[:ANSWERED_BY]->(a:Answer) MATCH (c:Chunk) WHERE c.chunk_id IN coalesce(a.cited_chunk_ids, []) MATCH (d:Document {doc_id:c.doc_id}) RETURN DISTINCT " + CHUNK_COLS, qid=qid, limit=limit))


def doc_entities(db: DB, ids: list[str]) -> list[dict]:
    rows = _safe(lambda: db.read("MATCH (d:Document) WHERE d.doc_id IN $ids RETURN d.doc_id AS doc_id, d.title AS title, d.year AS year, [(d)-[:TAGGED_WITH]->(t:Tag) | t.name] AS tags", ids=ids)) if ids else []
    for r in rows:
        r.setdefault("partners", [])
        r.setdefault("refs", [])
    return rows


def expand_graph(db: DB, doc_ids: list[str], limit: int = 6, two_hop: bool = True, corpus: str | None = None) -> list[dict]:
    if not doc_ids:
        return []
    return _safe(lambda: db.read("MATCH (d:Document) WHERE d.doc_id IN $ids MATCH (d)-[:TAGGED_WITH]->(t:Tag)<-[:TAGGED_WITH]-(o:Document) WHERE NOT o.doc_id IN $ids AND ($corpus IS NULL OR coalesce(o.corpus,o.domain,'bappenas')=$corpus) RETURN o.doc_id AS doc_id, o.title AS title, 1 AS hops, 'tag' AS via, [{kind:'Tag', name:t.name}] AS shared, 1.0 AS score LIMIT $limit", ids=doc_ids, limit=limit, corpus=corpus))


def related_docs(db: DB, doc_id: str, limit: int = 5, corpus: str | None = None) -> list[dict]:
    out = []
    for r in expand_graph(db, [doc_id], limit, corpus=corpus):
        out.append({"doc_id": r["doc_id"], "title": r["title"], "shared": [s["name"] for s in r["shared"]][:5], "n": len(r["shared"]), "hops": r["hops"], "via": r["via"]})
    return out


def entity_docs(db: DB, plan, limit: int = 12, corpus: str | None = None) -> list[dict]:
    q, out = lucene(plan.topic, fuzzy=True), []
    for kind in ("tag", "reference", "organization"):
        out += _ft(db, kind, "WITH node, score MATCH (d:Document)-[r:TAGGED_WITH|BELONGS_TO_ORG|IN_CATEGORY]->(node) WHERE $corpus IS NULL OR coalesce(d.corpus,d.domain,'bappenas')=$corpus RETURN labels(node)[0] AS kind, coalesce(node.name, node.title) AS entity, type(r) AS rel, r.role AS role, d.doc_id AS doc_id, d.title AS title, score", q, limit=limit, corpus=corpus)
    out.sort(key=lambda r: r["score"], reverse=True)
    return out[:limit * 2]


def by_topic(db: DB, topic: str, limit: int = 10) -> list[dict]:
    return _safe(lambda: db.read("MATCH (t:Tag) WHERE toLower(t.name) CONTAINS toLower($topic) MATCH (d:Document)-[r:TAGGED_WITH]->(t) RETURN t.name AS tag, d.doc_id AS doc_id, d.title AS title, d.year AS year, r.frequency AS frequency ORDER BY frequency DESC LIMIT $limit", topic=topic, limit=limit))