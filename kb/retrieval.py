"""Orkestrasi retrieval GraphRAG ARCANA: pertanyaan -> rencana -> dokumen -> bagian graf -> (hibrida | ekspansi) -> jawaban terstruktur + sitasi."""
from __future__ import annotations
import re
from . import search
from .config import S
from .chunker import lead
from .query_plan import OVERVIEW_SECTIONS, QueryPlan, analyze, fold, stem, terms
from .text import overlap

SECTION_LABEL = {
    "identitas": "Identitas dokumen", 
    "deskripsi": "Deskripsi", 
    "manfaat": "Manfaat", 
    "proses_bisnis": "Proses bisnis penyusunan",
    "regulasi": "Dasar hukum", 
    "data_sekunder": "Sumber data / rujukan", 
    "mitra": "Mitra dan kolaborasi", 
    "tag": "Kata kunci"
}

SEED_CAT_TO_INTENT = {
    "deskripsi": "deskripsi", 
    "manfaat": "manfaat", 
    "identitas": "identitas", 
    "proses": "proses", 
    "regulasi": "regulasi",
    "sumber": "sumber_data", 
    "mitra": "mitra", 
    "tag": "tag"
}


def strip_prefix(text: str, title: str) -> str:
    """Buang awalan template ('Manfaat dokumen "<judul>": ...') yang ditambahkan saat ingest; sisakan isinya."""
    t = " ".join((text or "").split())
    k = t.find(f'"{title}"')
    if 0 <= k <= 80:
        m = re.search(r":\s+", t[k + len(title) + 2:k + len(title) + 2 + 40])
        if m:
            return t[k + len(title) + 2 + m.end():].strip()
    return t


def sentences(text: str, min_len: int = 25) -> list[str]:
    parts = [p.strip() for p in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"(])", " ".join((text or "").split())) if p.strip()]
    out: list[str] = []
    for p in parts:
        if out and len(p) < min_len:
            out[-1] += " " + p
        else:
            out.append(p)
    return out


def best_passage(text: str, topic: list[str], n: int = 320) -> str:
    """Ambil kalimat (+ tetangganya) yang paling banyak memuat istilah pertanyaan."""
    ss = sentences(text, 1)
    if len(ss) <= 1 or not topic:
        return lead(text, n)
    qs = {stem(t) for t in topic if not t.isdigit()}
    sc = [sum(stem(w) in qs for w in terms(x)) for x in ss]
    i = max(range(len(ss)), key=lambda k: (sc[k], -k))
    out = ss[i]
    for j in (i + 1, i - 1):
        if len(out) < n * 0.6 and 0 <= j < len(ss):
            out = f"{out} {ss[j]}" if j > i else f"{ss[j]} {out}"
    return lead(out, n)


def bullets(items: list[str], cap: int | None = None, more: str = "lainnya") -> str:
    items = [i for i in items if i]
    shown = items[:cap] if cap else items
    s = "\n".join(f"- {i}" for i in shown)
    if cap and len(items) > cap:
        s += f"\n- _…dan {len(items) - cap} {more}_"
    return s


def _named_anchors(question: str) -> list[str]:
    return list(dict.fromkeys(re.findall(r"\b[A-Z][A-Z0-9]{1,}\b", question)))


def _anchor_forms(anchor: str) -> tuple[str, ...]:
    aliases = {
        "AI": ("AI", "artificial intelligence", "kecerdasan artifisial", "kecerdasan buatan"),
        "RAG": ("RAG", "retrieval augmented generation"),
        "UGM": ("UGM", "Universitas Gadjah Mada"),
        "NUS": ("NUS", "National University of Singapore"),
    }
    return aliases.get(anchor.upper(), (anchor,))


def _filter_named_anchors(question: str, hits: list[dict]) -> list[dict]:
    anchors = _named_anchors(question)
    if not anchors or not hits:
        return hits
    out = []
    for hit in hits:
        haystack = " ".join(str(hit.get(key) or "") for key in ("title", "file_name", "breadcrumb", "section", "description", "text")).casefold()
        def contains(form: str) -> bool:
            if len(form) <= 4 and form.upper() == form:
                return bool(re.search(rf"(?<![a-z0-9]){re.escape(form)}(?![a-z0-9])", haystack, re.I))
            return fold(form) in fold(haystack)
        if any(contains(form) for anchor in anchors for form in _anchor_forms(anchor)):
            out.append(hit)
    return out if out else hits


class CiteBook:
    """Penomoran sitasi [n] yang konsisten antara teks jawaban dan daftar sitasi."""

    def __init__(self):
        self.items: list[dict] = []
        self._idx: dict[str, int] = {}

    def add(self, ev: dict, snippet: str | None = None, score: float | None = None, extra_ids: list[str] | None = None, section: str | None = None) -> str:
        cid = ev["chunk_id"]
        if cid not in self._idx:
            source_no = len(self.items) + 1
            self.items.append({
                "doc_id": ev["doc_id"], 
                "title": ev["title"], 
                "chunk_id": cid,
                "source_id": f"S{source_no}",
                "breadcrumb": ev.get("breadcrumb") or ev["title"], 
                "page": ev.get("page"), 
                "url": ev.get("url") or None,
                "file_name": ev.get("file_name") or None, 
                "section": section or ev.get("section"),
                "retrieval_methods": ev.get("retrieval_methods") or ["graph_section"],
                "retrieval_scores": ev.get("retrieval_scores", {}),
                "graph_paths": ev.get("graph_paths", []),
                "snippet": snippet or lead(strip_prefix(ev["text"], ev["title"]), 300), 
                "score": round(float(score), 3) if score is not None else None,
                "chunk_ids": extra_ids or [cid], 
                "text": strip_prefix(ev["text"], ev["title"])
            })
            self._idx[cid] = len(self.items)
        return f"[{self._idx[cid]}]"


def pick_resolved(plan: QueryPlan, cands: list[dict]) -> list[dict]:
    if not cands:
        return []
    qn = [t for t in plan.topic if not t.isdigit()]
    top = cands[0]
    unique = len(cands) == 1 or cands[1]["rank"] < top["rank"] - 0.08
    confident = top["cover"] >= 0.4 and (len(qn) >= 1 or unique)
    if not confident:
        return []
    return [c for c in cands if c["cover"] >= 0.35 and c["rank"] >= top["rank"] - 0.1][:3]


def answer(db, question: str, top_k: int = 5, context_doc_ids: list[str] | None = None,
           corpus: str | None = None, document_id: str | None = None, generate_llm: bool = False,
           neighbor_window: int | None = None) -> dict:
    plan = analyze(question)
    trace: list[str] = []
    cb, res = CiteBook(), {"corpus": corpus or "all", "matched_question": None, "evidence": [], "suggestions": [], "context_doc_ids": []}

    if document_id:
        resolved = search.docs_by_ids(db, [document_id], corpus)
        cands = resolved
        trace.append("document_id_filter")
        for doc in resolved:
            doc.setdefault("cover", 1.0)
    else:
        cands, st = search.find_documents(db, plan, corpus=corpus) if plan.topic else ([], [])
        trace += st
        cands = _filter_named_anchors(question, cands)
        resolved = pick_resolved(plan, cands)

    if document_id and not resolved:
        resolved = search.docs_by_ids(db, [document_id], None)

    if document_id and resolved:
        hits, stages = search.search_chunks(db, plan, top_k, [document_id], corpus, restrict_doc_ids=False)
        trace.extend(stages)
        hits = _filter_named_anchors(question, hits)
        for hit in hits:
            cb.add(hit, snippet=best_passage(hit["text"], plan.topic), score=hit.get("score", 0.0))
        res.update(
            source="graph_chunks" if hits else "none", context_doc_ids=[document_id] if hits else [],
            citations=[{k: v for k, v in c.items() if k != "text"} for c in cb.items],
            plan={"intents": plan.intents, "sections": [], "topic": plan.topic, "year": plan.year,
                  "followup": False, "resolved": [document_id], "trace": trace})
    else:
        ctx = [d for d in (context_doc_ids or [])]
        weak = not cands or cands[0]["cover"] < 0.4
        if ctx and (plan.followup or (weak and plan.intents)) and not resolved:
            resolved = search.docs_by_ids(db, ctx[:1], corpus)
            if resolved:
                trace.append("konteks_percakapan")
                for d in resolved:
                    d.setdefault("cover", 1.0)

        if resolved:
            ids = [d["doc_id"] for d in resolved]
            chunk_hits, chunk_stages = search.search_chunks(
                db, plan, top_k, ids, corpus, restrict_doc_ids=S.graph_restrict_resolved
            )
            trace.extend(chunk_stages)
            chunk_hits = _filter_named_anchors(question, chunk_hits)
            if chunk_hits:
                for hit in chunk_hits:
                    cb.add(hit, snippet=best_passage(hit["text"], plan.topic), score=hit.get("score", 0.0))
                res.update(source="graph_chunks", context_doc_ids=list(dict.fromkeys(hit["doc_id"] for hit in chunk_hits)))
            else:
                plan.reintent(resolved[0]["title"])
                if not plan.sections:
                    plan.intents = ["ringkasan"]; plan.sections = list(OVERVIEW_SECTIONS)
                ev = search.section_chunks(db, ids, plan.sections)
                for e in ev:
                    cb.add(e, snippet=best_passage(e["text"], plan.topic, 500))
                res.update(source="graph_sections", context_doc_ids=ids)
        else:
            res.update(_open_question(db, plan, cands, cb, top_k, trace, question, corpus))

    cites = cb.items
    evidence = [
        {
            "n": i,
            "source_id": c.get("source_id", f"S{i}"),
            "title": c["title"],
            "section": c.get("section"),
            "breadcrumb": c.get("breadcrumb"),
            "page": c.get("page"),
            "url": c.get("url"),
            "file_name": c.get("file_name"),
            "text": c["text"],
            "doc_id": c["doc_id"],
            "chunk_id": c["chunk_id"],
            "score": c.get("score"),
            "retrieval_methods": c.get("retrieval_methods", []),
            "retrieval_scores": c.get("retrieval_scores", {}),
            "graph_paths": c.get("graph_paths", []),
        } for i, c in enumerate(cites, 1)
    ]
    # Traversal graf: tambahkan saudara berurutan (SUB_CHUNK_OF) sebagai konteks pendamping tiap chunk terpilih.
    selected_ids = {e["chunk_id"] for e in evidence}
    window = S.graph_neighbor_window if neighbor_window is None else neighbor_window
    neighbors = search.neighbor_chunks(db, list(selected_ids), window)
    for e in evidence:
        e["neighbors"] = [x for x in neighbors.get(e["chunk_id"], []) if x["chunk_id"] not in selected_ids and x["text"]]

    # Catatan: generasi LLM TIDAK dilakukan di sini. Satu-satunya pemanggilan Groq ada di kb_api (rag.generate)
    # agar konteks yang dicatat identik dengan konteks yang dikirim dan tidak ada panggilan ganda.
    answer_text = ""

    res.update(
        answer=answer_text,
        citations=[{k: v for k, v in c.items() if k != "text"} for c in cites],
        evidence=evidence,
        plan={"intents": plan.intents, "sections": plan.sections, "topic": plan.topic, "year": plan.year, "followup": plan.followup,
              "resolved": [d["doc_id"] for d in resolved], "trace": trace}
    )
    return res


def answer_vector_only(db, question: str, top_k: int = 5, corpus: str | None = None,
                       document_id: str | None = None, context_doc_ids: list[str] | None = None, generate_llm: bool = False) -> dict:
    followup_plan = analyze(question)
    prior_doc_id = (context_doc_ids or [None])[0] if followup_plan.followup else None
    scope_doc_id = document_id or prior_doc_id

    hits = search.vector_only_chunks(db, question, max(top_k * 20, 100), corpus, scope_doc_id)
    hits = search.rerank_vector_hits(question, hits)
    hits = _filter_named_anchors(question, hits)
    hits = hits[:top_k]

    citations, evidence = [], []
    for hit in hits:
        text = (hit.get("text") or "").strip()
        passage = best_passage(text, terms(question), 520)
        index = len(evidence) + 1
        citations.append({
            "source_id": f"S{index}", "doc_id": hit["doc_id"], "title": hit["title"], "chunk_id": hit["chunk_id"],
            "breadcrumb": hit.get("breadcrumb"), "page": hit.get("page"), "url": hit.get("url"),
            "snippet": passage, "score": float(hit.get("score") or 0.0), "section": hit.get("section"),
            "file_name": hit.get("file_name"), "retrieval_methods": ["vector"],
            "retrieval_scores": {"vector": float(hit.get("score") or 0.0)},
        })
        evidence.append({
            "n": index, "source_id": f"S{index}", "title": hit["title"], "section": hit.get("section"),
            "breadcrumb": hit.get("breadcrumb"), "page": hit.get("page"), "url": hit.get("url"),
            "file_name": hit.get("file_name"), "text": text, "doc_id": hit["doc_id"], "chunk_id": hit["chunk_id"],
            "score": float(hit.get("score") or 0.0), "retrieval_methods": ["vector"],
            "retrieval_scores": {"vector": float(hit.get("score") or 0.0)}, "graph_paths": []
        })

    answer_text = ""   # generasi dilakukan satu kali di kb_api (rag.generate)

    best_score = max((float(hit.get("score") or 0.0) for hit in hits), default=0.0)
    return {
        "answer": answer_text, "source": "vector_chunks", "corpus": corpus,
        "context_doc_ids": list(dict.fromkeys(hit["doc_id"] for hit in hits)),
        "citations": citations, "evidence": evidence,
        "plan": {"trace": ["vector_only"], "resolved": [scope_doc_id] if scope_doc_id else [],
                 "best_similarity": round(best_score, 4), "evidence_sufficient": bool(hits)},
    }


def _open_question(db, plan: QueryPlan, cands: list[dict], cb: CiteBook, top_k: int, trace: list[str], question: str, corpus: str | None = None) -> dict:
    out = {"source": "none", "context_doc_ids": []}
    hits, st = search.search_chunks(db, plan, top_k, [d["doc_id"] for d in cands[:5]] if cands else None,
                                    corpus, restrict_doc_ids=False)
    hits = _filter_named_anchors(question, hits)
    trace += st
    if hits:
        ids = list(dict.fromkeys(h["doc_id"] for h in hits))
        for hit in hits:
            cb.add(hit, snippet=best_passage(hit["text"], plan.topic), score=hit.get("score", 0.0))
        out.update(source="chunks", context_doc_ids=ids[:3], expansion=[], suggestions=[f"Jelaskan isi {hits[0]['title']}"])
        return out

    ents = search.entity_docs(db, plan, corpus=corpus)
    if ents:
        trace.append("entity_docs")
        ids = list(dict.fromkeys(e["doc_id"] for e in ents))[:5]
        chunk_hits, _ = search.search_chunks(db, plan, top_k, ids, corpus, restrict_doc_ids=False)
        for hit in chunk_hits:
            cb.add(hit, snippet=best_passage(hit["text"], plan.topic), score=hit.get("score", 0.0))
        out.update(source="entity_chunks", context_doc_ids=ids[:3])
        return out

    return out