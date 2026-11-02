"""
Loader terpadu (identik untuk Bappenas & Bencana):
metadata (+ berkas fisik) -> graf Neo4j sesuai kb.ontology.

Idempoten (MERGE), tiap Cypher divalidasi `ontology.check`
(label/relasi di luar skema terpadu ditolak).

Neo4j menggunakan konfigurasi dari .env / config.py.
Untuk deployment kamu, gunakan Neo4j Aura.
"""

from __future__ import annotations

import json
import hashlib
import time
import traceback
from pathlib import Path

from . import crosslink, metadata as _md, ontology
from .chunker import build_chunks
from .config import S
from .db import DB
from .embeddings import embed
from .extract import extract_blocks, find_file
from .metadata import H, load_docs, metadata_blocks
from .notetaker import load_notetaker_docs


# Hanya domain bencana yang memiliki fakta baris tabel.
extract_facts = getattr(
    _md,
    "extract_facts",
    lambda text: {},
)

INGEST_VERSION = "3"  # transcript-aware atomic turns changed chunk boundaries


def _ingest_fingerprint(d: dict) -> str:
    """Hash inputs and chunking/embedding settings to detect changed documents."""
    source_dir = S.notetaker_markdown_dir if d.get("corpus") == "notetaker" else S.docs_dir
    source_file = find_file(source_dir, d.get("file_name", ""))
    input_paths = [source_file] if source_file else []
    if d.get("corpus") == "notetaker":
        sidecar = S.notetaker_json_dir / f'{Path(d.get("file_name", "")).stem}.json'
        if sidecar.exists():
            input_paths.append(sidecar)
    settings = {
        "version": INGEST_VERSION,
        "max_chunk_chars": S.max_chunk_chars,
        "fanout": S.fanout,
        "max_chunks_per_doc": S.max_chunks_per_doc,
        "embeddings": S.embeddings,
        "embedding_model": S.embedding_model if S.embeddings else None,
        "embedding_dim": S.embedding_dim if S.embeddings else None,
    }
    digest = hashlib.sha256()
    digest.update(json.dumps({"document": d, "settings": settings}, ensure_ascii=False,
                             sort_keys=True, default=str).encode("utf-8"))
    for path in sorted(input_paths, key=lambda item: item.name):
        digest.update(path.name.encode("utf-8"))
        with path.open("rb") as source:
            for block in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(block)
    return digest.hexdigest()


def _ingest_is_complete(db: DB, doc_id: str, fingerprint: str) -> str | None:
    rows = db.read("""
        MATCH (d:Document {doc_id:$doc_id})
        OPTIONAL MATCH (c:Chunk {doc_id:$doc_id})
        RETURN d.ingest_status AS status, d.ingest_hash AS ingest_hash,
               d.ingest_chunk_count AS expected_chunks, count(c) AS actual_chunks,
               coalesce(sum(CASE WHEN c.embedding IS NOT NULL THEN 1 ELSE 0 END), 0) AS embedded_chunks
    """, doc_id=doc_id)
    if not rows:
        return None
    row = rows[0]
    expected = row.get("expected_chunks") or 0
    actual = row.get("actual_chunks") or 0
    embedded = row.get("embedded_chunks") or 0
    if row.get("status") is None and actual > 0 and (not S.embeddings or embedded == actual):
        _set_ingest_status(db, doc_id, fingerprint, "complete", actual)
        return "adopted"
    if (
        row.get("status") == "complete"
        and row.get("ingest_hash") == fingerprint
        and expected > 0
        and actual == expected
        and (not S.embeddings or embedded == expected)
    ):
        return "unchanged"
    return None


def _set_ingest_status(db: DB, doc_id: str, fingerprint: str, status: str,
                       chunk_count: int | None = None, error: str | None = None) -> None:
    db.write("""
        MERGE (d:Document {doc_id:$doc_id})
        SET d.ingest_status=$status, d.ingest_hash=$fingerprint,
            d.ingest_updated_at=timestamp(), d.ingest_chunk_count=$chunk_count,
            d.ingest_error=$error
    """, doc_id=doc_id, fingerprint=fingerprint, status=status,
         chunk_count=chunk_count, error=error)


def _crosslink_state_id(notetaker_only: bool) -> str:
    return "notetaker" if notetaker_only else "all"


def _crosslinks_pending(db: DB, state_id: str) -> bool:
    rows = db.read("""
        MATCH (s:IngestState {state_id:$state_id})
        RETURN s.crosslink_status AS status
    """, state_id=state_id)
    return bool(rows and rows[0].get("status") == "pending")


def _set_crosslink_status(db: DB, state_id: str, status: str) -> None:
    db.write("""
        MERGE (s:IngestState {state_id:$state_id})
        SET s.crosslink_status=$status, s.crosslink_updated_at=timestamp()
    """, state_id=state_id, status=status)


# ============================================================
# HELPER DATABASE WRITE
# ============================================================

def _w(db: DB, cypher: str, **p):
    """
    Jalankan Cypher yang sudah divalidasi ontology.

    Parameter sebelumnya bernama `q`, tetapi itu bentrok dengan
    parameter Cypher `q` yang digunakan pada load_seed().
    Diganti menjadi `cypher` agar pemanggilan seperti:

        _w(db, "...", q=it["question"])

    tetap valid.
    """
    return db.write(
        ontology.check(cypher),
        **p,
    )


# ============================================================
# DOCUMENT BLOCKS
# ============================================================

def doc_blocks(
    d: dict,
) -> tuple[list[dict], Path | None, str | None]:
    blocks = metadata_blocks(d)
    source_dir = S.notetaker_markdown_dir if d.get("corpus") == "notetaker" else S.docs_dir
    f = find_file(source_dir, d["file_name"])
    err = None

    if f:
        try:
            fb = extract_blocks(f)

            for b in fb:
                if b["kind"] == "h":
                    b["level"] = min(
                        b["level"] + 1,
                        8,
                    )

            blocks += [
                H(1, f"Isi Dokumen: {f.name}")
            ] + fb

        except Exception as e:  # noqa: BLE001
            err = f"{f.name}: {e}"

    return blocks, f, err


# ============================================================
# DOCUMENT CYPHER STATEMENTS
# ============================================================

def _doc_stmts(
    d: dict,
    has_file: bool,
    tag_freq: dict[str, int],
) -> list[tuple[str, dict]]:

    g = ontology.to_generic(d)
    did = d["doc_id"]
    st = []

    # --------------------------------------------------------
    # Document
    # --------------------------------------------------------

    st.append(
        (
            """
            MERGE (d:Document {doc_id:$doc_id})
            SET d.title=$title,
                d.corpus=$corpus,
                d.file_name=$file_name,
                d.file_type=$file_type,
                d.output_type=$output_type,
                d.knowledge_type=$knowledge_type,
                d.description=$description,
                d.benefit=$benefit,
                d.classification=$classification,
                d.access_rights=$access_rights,
                d.document_url=$document_url,
                d.year=$year,
                d.domain=$domain,
                d.has_physical_file=$has_file,
                d.category=$category,
                d.subcategory=$subcategory,
                d.publish_date =
                    CASE
                        WHEN $publish_date IS NULL
                        THEN null
                        ELSE date($publish_date)
                    END
            SET d += $extra
            """,
            {
                **{
                    k: d.get(k)
                    for k in (
                        "doc_id",
                        "title",
                        "file_name",
                        "file_type",
                        "output_type",
                        "knowledge_type",
                        "description",
                        "benefit",
                        "classification",
                        "access_rights",
                        "document_url",
                        "year",
                        "domain",
                        "publish_date",
                        "category",
                        "subcategory",
                    )
                },
                "corpus": d.get("corpus") or d.get("domain") or "bappenas",
                "has_file": has_file,
                "extra": g["extra"],
            },
        )
    )

    # --------------------------------------------------------
    # Organization
    # --------------------------------------------------------

    st.append(
        (
            """
            UNWIND $rows AS o
            MERGE (x:Organization {org_id:o.org_id})
            ON CREATE SET
                x.name=o.name,
                x.org_type=o.org_type,
                x.level=o.level,
                x.scope=o.scope,
                x.kontak=o.kontak
            """,
            {
                "rows": g["orgs"],
            },
        )
    )

    # --------------------------------------------------------
    # Document -> Organization
    # --------------------------------------------------------

    st.append(
        (
            """
            UNWIND $rows AS r
            MATCH (d:Document {doc_id:$doc_id})
            MATCH (x:Organization {org_id:r.org_id})
            MERGE (d)-[b:BELONGS_TO_ORG {role:r.role}]->(x)
            SET b.detail=r.detail
            """,
            {
                "rows": g["doc_orgs"],
                "doc_id": did,
            },
        )
    )

    # --------------------------------------------------------
    # Organization hierarchy
    # --------------------------------------------------------

    if g["org_orgs"]:
        st.append(
            (
                """
                UNWIND $rows AS r
                MATCH (c:Organization {org_id:r.child})
                MATCH (p:Organization {org_id:r.parent})
                MERGE (c)-[b:BELONGS_TO_ORG {role:r.role}]->(p)
                SET b.level_path=r.level_path
                """,
                {
                    "rows": g["org_orgs"],
                },
            )
        )

    # --------------------------------------------------------
    # Category
    # --------------------------------------------------------

    if g["category"]:
        st.append(
            (
                """
                MERGE (c:Category {name:$c})
                WITH c
                MATCH (d:Document {doc_id:$doc_id})
                MERGE (d)-[:IN_CATEGORY]->(c)
                """,
                {
                    "c": g["category"],
                    "doc_id": did,
                },
            )
        )

    # --------------------------------------------------------
    # SubCategory
    # --------------------------------------------------------

    if g["subcategories"]:
        st.append(
            (
                """
                UNWIND $rows AS s
                MERGE (x:SubCategory {name:s.name})
                WITH x, s
                MATCH (d:Document {doc_id:$doc_id})
                MERGE (d)-[:IN_CATEGORY]->(x)
                WITH x, s
                OPTIONAL MATCH (c:Category {name:s.parent})
                FOREACH (
                    _ IN CASE
                        WHEN c IS NULL
                        THEN []
                        ELSE [1]
                    END |
                    MERGE (x)-[:SUBCATEGORY_OF]->(c)
                )
                """,
                {
                    "rows": g["subcategories"],
                    "doc_id": did,
                },
            )
        )

    # --------------------------------------------------------
    # References
    # --------------------------------------------------------

    if g["references"]:
        st.append(
            (
                """
                UNWIND $rows AS r
                MERGE (x:Reference {ref_id:r.ref_id})
                ON CREATE SET
                    x.title=r.title,
                    x.ref_type=r.ref_type
                WITH x, r
                MATCH (d:Document {doc_id:$doc_id})
                MERGE (d)-[u:TAGGED_WITH {role:r.role}]->(x)
                """,
                {
                    "rows": g["references"],
                    "doc_id": did,
                },
            )
        )

    # --------------------------------------------------------
    # Process Steps
    # --------------------------------------------------------

    if g["steps"]:
        st.append(
            (
                """
                UNWIND $rows AS r
                MERGE (s:ProcessStep {step_id:r.sid})
                SET
                    s.step_order=r.n,
                    s.description=r.t
                WITH s, r
                MATCH (d:Document {doc_id:$doc_id})
                MERGE (d)-[x:CONTAINS_STEP]->(s)
                SET x.step_no=r.n
                """,
                {
                    "rows": [
                        {
                            "sid": f"{did}_S{i}",
                            "n": i,
                            "t": t,
                        }
                        for i, t in enumerate(
                            g["steps"],
                            1,
                        )
                    ],
                    "doc_id": did,
                },
            )
        )

    # --------------------------------------------------------
    # Location
    # --------------------------------------------------------

    st += _location_stmts(
        g["locations"],
    )

    st.append(
        (
            """
            UNWIND $rows AS l
            MATCH (x:Location {name:l.name})
            WITH x
            MATCH (d:Document {doc_id:$doc_id})
            MERGE (d)-[:LOCATED_IN]->(x)
            """,
            {
                "rows": g["locations"],
                "doc_id": did,
            },
        )
    )

    # --------------------------------------------------------
    # Tags
    # --------------------------------------------------------

    if g["tags"]:
        st.append(
            (
                """
                UNWIND $rows AS r
                MERGE (t:Tag {name:r.t})
                ON CREATE SET t.kind=r.kind
                WITH t, r
                MATCH (d:Document {doc_id:$doc_id})
                MERGE (d)-[x:TAGGED_WITH]->(t)
                SET x.frequency=r.f
                """,
                {
                    "rows": [
                        {
                            "t": t,
                            "kind": k,
                            "f": tag_freq.get(t, 1),
                        }
                        for t, k in g["tags"]
                    ],
                    "doc_id": did,
                },
            )
        )

    return st


# ============================================================
# LOCATION
# ============================================================

def _location_stmts(
    locs: list[dict],
) -> list[tuple[str, dict]]:

    st = [
        (
            """
            UNWIND $rows AS l
            MERGE (x:Location {name:l.name})
            ON CREATE SET
                x.level=l.level,
                x.code=l.code,
                x.parent=l.parent
            """,
            {
                "rows": locs,
            },
        )
    ]

    edges = [
        {
            "c": l["name"],
            "p": l["parent"],
        }
        for l in locs
        if l.get("parent")
    ]

    if edges:
        st.append(
            (
                """
                UNWIND $rows AS e
                MATCH (c:Location {name:e.c})
                MATCH (p:Location {name:e.p})
                MERGE (c)-[:LOCATED_IN]->(p)
                """,
                {
                    "rows": edges,
                },
            )
        )

    return st


# ============================================================
# FACT LOCATIONS
# ============================================================

def _fact_locations(
    facts_rows: list[dict],
) -> tuple[list[dict], list[dict]]:

    """
    Fakta baris tabel -> Location berjenjang
    (kelurahan > kecamatan > kota > provinsi)
    + tautan chunk.
    """

    nodes = {}
    links = []

    for r in facts_rows:
        f = r["facts"]
        chain = []

        for lvl, key, pre in (
            ("kelurahan", "kelurahan", "Kelurahan "),
            ("kecamatan", "kecamatan", "Kecamatan "),
            ("kota", "kota", ""),
        ):
            if f.get(key):
                chain.append(
                    {
                        "name": f"{pre}{f[key]}",
                        "level": lvl,
                        "code": None,
                    }
                )

        if not chain:
            continue

        chain.append(
            {
                "name": "Provinsi DKJ",
                "level": "provinsi",
                "code": "32010026",
            }
        )

        for a, b in zip(
            chain,
            chain[1:],
        ):
            nodes[a["name"]] = {
                **a,
                "parent": b["name"],
            }

        nodes.setdefault(
            "Provinsi DKJ",
            {
                **chain[-1],
                "parent": None,
            },
        )

        links.append(
            {
                "chunk_id": r["chunk_id"],
                "loc": chain[0]["name"],
            }
        )

    return list(nodes.values()), links


# ============================================================
# BATCH HELPER
# ============================================================

def _batches(
    rows: list,
    n: int = 400,
):
    for i in range(
        0,
        len(rows),
        n,
    ):
        yield rows[i : i + n]


# ============================================================
# INGEST DOCUMENT
# ============================================================

def ingest_document(
    db: DB,
    d: dict,
) -> dict:

    blocks, f, ferr = doc_blocks(d)

    chunks = build_chunks(
        d["doc_id"],
        d["title"],
        blocks,
        S.max_chunk_chars,
        S.fanout,
        S.max_chunks_per_doc,
    )

    vecs = (
        embed(
            [c.text for c in chunks]
        )
        if S.embeddings
        else None
    )
    if S.embeddings and (not vecs or len(vecs) != len(chunks)):
        raise RuntimeError("Embedding chunk tidak lengkap; ingest dihentikan sebelum mengganti data lama.")

    rows = [
        {
            **c.__dict__,
            "page": c.page,
            "embedding": (
                vecs[i]
                if vecs
                else None
            ),
            "corpus": d.get("corpus") or d.get("domain") or "bappenas",
            "facts": (
                extract_facts(c.text)
                if c.is_leaf
                else {}
            ),
        }
        for i, c in enumerate(chunks)
    ]

    # --------------------------------------------------------
    # Tag frequency
    # --------------------------------------------------------

    low = {
        c.chunk_id: c.text.lower()
        for c in chunks
    }

    ctags = []
    dfreq = {}

    g = ontology.to_generic(d)

    for t, _ in g["tags"]:
        tot = 0

        for cid, txt in low.items():
            n = txt.count(
                t.lower()
            )

            if n:
                tot += n
                ctags.append(
                    {
                        "chunk_id": cid,
                        "tag": t,
                        "freq": n,
                    }
                )

        dfreq[t] = max(
            tot,
            1,
        )

    # --------------------------------------------------------
    # Remove old chunks
    # --------------------------------------------------------

    _w(
        db,
        """
        MATCH (c:Chunk {doc_id:$d})
        DETACH DELETE c
        """,
        d=d["doc_id"],
    )

    # --------------------------------------------------------
    # Document metadata
    # --------------------------------------------------------

    db.write_many(
        [
            (
                ontology.check(q),
                p,
            )
            for q, p in _doc_stmts(
                d,
                bool(f),
                dfreq,
            )
        ]
    )

    # --------------------------------------------------------
    # Chunk nodes
    # --------------------------------------------------------

    for b in _batches(rows):
        _w(
            db,
            """
            UNWIND $rows AS r
            MERGE (c:Chunk {chunk_id:r.chunk_id})
            SET
                c.doc_id=r.doc_id,
                c.corpus=r.corpus,
                c.text=r.text,
                c.level=r.level,
                c.chunk_index=r.chunk_index,
                c.token_count=r.token_count,
                c.page_number=r.page,
                c.breadcrumb=r.breadcrumb,
                c.section=r.section,
                c.item_no=r.item_no,
                c.is_leaf=r.is_leaf,
                c.embedding=r.embedding
            SET c += r.facts
            """,
            rows=b,
        )

    # --------------------------------------------------------
    # Document -> Chunk
    # --------------------------------------------------------

    for b in _batches(
        [
            r
            for r in rows
            if r["parent_id"] is None
        ]
    ):
        _w(
            db,
            """
            UNWIND $rows AS r
            MATCH (d:Document {doc_id:r.doc_id})
            MATCH (c:Chunk {chunk_id:r.chunk_id})
            MERGE (d)-[x:CONTAINS_CHUNK]->(c)
            SET x.sequence=r.chunk_index
            """,
            rows=b,
        )

    # --------------------------------------------------------
    # Chunk hierarchy
    # --------------------------------------------------------

    for b in _batches(
        [
            r
            for r in rows
            if r["parent_id"]
        ]
    ):
        _w(
            db,
            """
            UNWIND $rows AS r
            MATCH (c:Chunk {chunk_id:r.chunk_id})
            MATCH (p:Chunk {chunk_id:r.parent_id})
            MERGE (c)-[x:SUB_CHUNK_OF]->(p)
            SET
                x.order=r.chunk_index,
                x.level_diff=1
            """,
            rows=b,
        )

    # --------------------------------------------------------
    # Chunk tags
    # --------------------------------------------------------

    for b in _batches(ctags):
        _w(
            db,
            """
            UNWIND $rows AS r
            MATCH (c:Chunk {chunk_id:r.chunk_id})
            MERGE (t:Tag {name:r.tag})
            ON CREATE SET t.kind='kata_kunci'
            MERGE (c)-[x:TAGGED_WITH]->(t)
            SET x.frequency=r.freq
            """,
            rows=b,
        )

    # --------------------------------------------------------
    # Facts -> Locations
    # --------------------------------------------------------

    frows = [
        r
        for r in rows
        if r["facts"]
    ]

    nodes, links = _fact_locations(
        frows,
    )

    if nodes:
        for q, p in _location_stmts(
            nodes
        ):
            _w(
                db,
                q,
                **p,
            )

        for b in _batches(links):
            _w(
                db,
                """
                UNWIND $rows AS r
                MATCH (c:Chunk {chunk_id:r.chunk_id})
                MATCH (l:Location {name:r.loc})
                MERGE (c)-[:LOCATED_IN]->(l)
                """,
                rows=b,
            )

    # --------------------------------------------------------
    # Report per document
    # --------------------------------------------------------

    lv = [
        c.level
        for c in chunks
    ]

    return {
        "doc_id": d["doc_id"],
        "title": d["title"],
        "physical_file": (
            f.name
            if f
            else None
        ),
        "file_error": ferr,
        "chunks": len(chunks),
        "table_facts": len(frows),
        "max_level": max(lv)
        if lv
        else 0,
        "leaf": sum(
            c.is_leaf
            for c in chunks
        ),
        "status": "incomplete" if ferr else "complete",
    }


# ============================================================
# CROSS DOCUMENT LINKING
# ============================================================

def link_documents(
    db: DB,
    corpus: str | None = None,
) -> int:

    rows = db.read(
        """
        MATCH (c:Chunk)
        WHERE $corpus IS NULL OR c.corpus=$corpus
        RETURN
            c.chunk_id AS chunk_id,
            c.doc_id AS doc_id,
            c.text AS text,
            c.section AS section
        """,
        corpus=corpus,
    )

    links = crosslink.compute(
        rows,
        S.crosslink_topk,
        S.crosslink_min_sim,
    )

    # Bersihkan REFERENCES_CHUNK lama.
    _w(
        db,
        """
        MATCH (a:Chunk)-[r:REFERENCES_CHUNK]->(b:Chunk)
        WHERE $corpus IS NULL OR a.corpus=$corpus OR b.corpus=$corpus
        DELETE r
        """,
        corpus=corpus,
    )

    for b in _batches(
        links,
        500,
    ):
        _w(
            db,
            """
            UNWIND $rows AS r
            MATCH (a:Chunk {chunk_id:r.src})
            MATCH (b:Chunk {chunk_id:r.dst})
            MERGE (a)-[x:REFERENCES_CHUNK]->(b)
            SET
                x.similarity=r.similarity,
                x.type=r.type
            """,
            rows=b,
        )

    return len(links)


# ============================================================
# SEED QUESTION / ANSWER
# ============================================================

def load_seed(
    db: DB,
    path: Path | None = None,
) -> int:

    """
    Question -ANSWERED_BY-> Answer
    Question -ASKED_ABOUT-> Document|Chunk

    ID chunk sumber juga disimpan di:
        Answer.cited_chunk_ids
    """

    path = path or S.seed_json

    if not path.exists():
        return 0

    items = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    for it in items:

        # ----------------------------------------------------
        # Question -> Answer
        # ----------------------------------------------------

        _w(
            db,
            """
            MERGE (q:Question {question_id:$qid})
            SET
                q.text=$q,
                q.corpus=$corpus,
                q.status=$status,
                q.category=$cat

            MERGE (a:Answer {answer_id:$aid})
            SET
                a.text=$a,
                a.cited_chunk_ids=[]

            MERGE (q)-[:ANSWERED_BY]->(a)
            """,
            qid=it["question_id"],
            corpus=it.get("corpus", "bappenas"),
            q=it["question"],
            status=it.get(
                "status",
                "draft",
            ),
            cat=it.get(
                "category",
                "",
            ),
            aid=it["question_id"].replace(
                "Q",
                "A",
                1,
            ),
            a=it["answer"],
        )

        # ----------------------------------------------------
        # Question -> Document / Chunk
        # ----------------------------------------------------

        for c in it["cites"]:

            _w(
                db,
                """
                MATCH (q:Question {question_id:$qid})
                    -[:ANSWERED_BY]->
                    (a:Answer)

                MATCH (d:Document {doc_id:$doc})

                MERGE (q)-[:ASKED_ABOUT]->(d)

                WITH q, a

                OPTIONAL MATCH (
                    c:Chunk {
                        doc_id:$doc,
                        section:$sec
                    }
                )

                WHERE
                    $item IS NULL
                    OR c.item_no=$item

                FOREACH (
                    x IN CASE
                        WHEN c IS NULL
                        THEN []
                        ELSE [c]
                    END |
                    MERGE (q)-[:ASKED_ABOUT]->(x)
                )

                WITH a, collect(c.chunk_id) AS ids

                SET a.cited_chunk_ids =
                    a.cited_chunk_ids +
                    [
                        i IN ids
                        WHERE NOT i IN a.cited_chunk_ids
                    ]
                """,
                qid=it["question_id"],
                doc=c["doc_id"],
                sec=c["section"],
                item=c.get(
                    "item"
                ),
            )

    return len(items)


# ============================================================
# MAIN RUN
# ============================================================

def run(
    only: list[str] | None = None,
    seed: bool = True,
    notetaker_only: bool = False,
    force: bool = False,
) -> dict:

    t0 = time.time()

    # DB() mengambil konfigurasi Neo4j dari config/.env.
    # Untuk project ini gunakan Neo4j Aura.
    db = DB()

    # Tunggu sampai koneksi Neo4j siap.
    db.wait_ready()

    from scripts.run_schema import apply_schema

    # --------------------------------------------------------
    # Apply graph schema
    # --------------------------------------------------------

    apply_schema(db)

    # --------------------------------------------------------
    # Load document metadata
    # --------------------------------------------------------

    source_docs = (
        load_notetaker_docs()
        if notetaker_only
        else load_docs(S.metadata_json)
    )
    for doc in source_docs:
        doc.setdefault("corpus", doc.get("domain") or "bappenas")
    docs = [
        d
        for d in source_docs
        if (
            not only
            or d["doc_id"] in only
        )
    ]

    report = []
    skipped = []
    adopted = []
    errors = []

    # --------------------------------------------------------
    # Ingest documents
    # --------------------------------------------------------

    for d in docs:

        try:
            fingerprint = None
            fingerprint = _ingest_fingerprint(d)
            skip_reason = None if force else _ingest_is_complete(db, d["doc_id"], fingerprint)
            if skip_reason:
                skipped.append(d["doc_id"])
                if skip_reason == "adopted":
                    adopted.append(d["doc_id"])
                    print(f'[adopt] {d["doc_id"]}: chunk lama terverifikasi, fingerprint awal dicatat')
                else:
                    print(f'[skip] {d["doc_id"]}: ingest lengkap dan sumber tidak berubah')
                continue

            _set_ingest_status(db, d["doc_id"], fingerprint, "processing")
            result = ingest_document(db, d)
            _set_ingest_status(db, d["doc_id"], fingerprint, result["status"],
                               result["chunks"], result.get("file_error"))
            if result["chunks"]:
                _set_crosslink_status(db, _crosslink_state_id(notetaker_only), "pending")
            report.append(result)
            if result["status"] == "complete":
                print(f'[ok] {d["doc_id"]} chunks={result["chunks"]} depth={result["max_level"]}')
            else:
                print(f'[incomplete] {d["doc_id"]}: {result["file_error"]}')

        except Exception as e:  # noqa: BLE001

            try:
                if fingerprint:
                    _set_ingest_status(db, d["doc_id"], fingerprint, "failed", error=str(e))
            except Exception:  # noqa: BLE001
                pass

            errors.append(
                {
                    "doc_id": d["doc_id"],
                    "error": str(e),
                    "trace": traceback.format_exc()[
                        -600:
                    ],
                }
            )

            print(
                f'[ERR] {d["doc_id"]}: {e}'
            )

    # --------------------------------------------------------
    # Cross document references
    # --------------------------------------------------------

    link_state_id = _crosslink_state_id(notetaker_only)
    refreshed_crosslinks = _crosslinks_pending(db, link_state_id)
    n_links = 0
    if refreshed_crosslinks:
        n_links = link_documents(db, "notetaker" if notetaker_only else None)
        _set_crosslink_status(db, link_state_id, "complete")

    # --------------------------------------------------------
    # Seed Question / Answer
    # --------------------------------------------------------

    n_seed = (
        load_seed(db)
        if seed
        else 0
    )

    # --------------------------------------------------------
    # Node counts
    # --------------------------------------------------------

    counts = {
        r["l"]: r["n"]
        for r in db.read(
            """
            MATCH (n)
            UNWIND labels(n) AS l
            RETURN l, count(*) AS n
            ORDER BY l
            """
        )
    }

    # --------------------------------------------------------
    # Relationship counts
    # --------------------------------------------------------

    rels = {
        r["t"]: r["n"]
        for r in db.read(
            """
            MATCH ()-[r]->()
            RETURN type(r) AS t, count(*) AS n
            ORDER BY t
            """
        )
    }

    # --------------------------------------------------------
    # Output report
    # --------------------------------------------------------

    out = {
        "seconds": round(
            time.time() - t0,
            1,
        ),
        "documents": len(report),
        "discovered_documents": len(docs),
        "skipped_documents": skipped,
        "adopted_legacy_documents": adopted,
        "crosslinks_refreshed": refreshed_crosslinks,
        "errors": errors,
        "crosslinks": n_links,
        "seed_qa": n_seed,
        "node_counts": counts,
        "rel_counts": rels,
        "per_document": report,
    }

    S.reports_dir.mkdir(
        exist_ok=True
    )

    (
        S.reports_dir
        / "ingest_report.json"
    ).write_text(
        json.dumps(
            out,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    # --------------------------------------------------------
    # Markdown report
    # --------------------------------------------------------

    md = [
        "# Laporan Muat Graf",
        (
            f"- Ditemukan: {len(docs)} "
            f"| Diproses: {len(report)} "
            f"| Dilewati: {len(skipped)} "
            f"| Gagal: {len(errors)} "
            f"| Crosslink: {n_links} "
            f"| Seed QA: {n_seed} "
            f"| {out['seconds']}s"
        ),
        "",
        (
            "| Dokumen | Berkas fisik | Chunk | "
            "Fakta tabel | Kedalaman | Daun |"
        ),
        "|---|---|---|---|---|---|",
    ]

    md += [
        (
            f'| {r["doc_id"]} '
            f'{r["title"][:50]} | '
            f'{r["physical_file"] or "-"} | '
            f'{r["chunks"]} | '
            f'{r["table_facts"]} | '
            f'{r["max_level"]} | '
            f'{r["leaf"]} |'
        )
        for r in report
    ]

    md += [
        "",
        "## Node",
        *[
            f"- {k}: {v}"
            for k, v in counts.items()
        ],
        "",
        "## Relasi",
        *[
            f"- {k}: {v}"
            for k, v in rels.items()
        ],
    ]

    (
        S.reports_dir
        / "ingest_report.md"
    ).write_text(
        "\n".join(md),
        encoding="utf-8",
    )

    # --------------------------------------------------------
    # Close Neo4j connection
    # --------------------------------------------------------

    db.close()

    return out
