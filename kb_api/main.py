"""FastAPI KB: Graph RAG and vector-only RAG query endpoints over Neo4j."""
from __future__ import annotations
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import json
import re
import threading
import time
import uuid
import traceback
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from kb import cross_document, rag, retrieval, search
from kb.config import S
from kb.db import DB

state: dict = {}
_query_log_lock = threading.Lock()


def get_db() -> DB:
    if "db" not in state:
        state["db"] = DB()
    return state["db"]


@asynccontextmanager
async def lifespan(app):
    yield
    if "db" in state:
        state["db"].close()

app = FastAPI(title="ARCANA Knowledge Graph External Knowledge Base API", version="1.1.0", lifespan=lifespan)


class QueryReq(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    top_k: int = Field(5, ge=1, le=15)
    # Corpus/domain names are deployment configuration, not a closed code enum.
    corpus: str | None = Field(None, min_length=1, max_length=100)
    document_id: str | None = Field(None, min_length=1, max_length=200)
    mode: str = Field("graph", pattern="^(graph|vector)$")
    context_doc_ids: list[str] = Field(default_factory=list, max_length=5)
    include_graph: bool = True
    debug: bool = False
    # Opsional (eksperimen terkontrol). None = perilaku sistem aktual.
    neighbor_window: int | None = Field(None, ge=0, le=3)
    context_chars: int | None = Field(None, ge=500, le=60000)


class CrossDocumentReq(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    top_k: int = Field(8, ge=1, le=30)
    corpus: str | None = Field(None, min_length=1, max_length=100)
    document_ids: list[str] = Field(default_factory=list, max_length=100)
    document_type: str | None = Field(None, max_length=100)


@app.post("/kb/retrieve/cross-document")
def cross_document_retrieve(req: CrossDocumentReq):
    """Return evidence spanning documents and the graph links used to expand retrieval."""
    started = time.perf_counter()
    try:
        result = cross_document.retrieve(get_db(), req.question, req.top_k,
                                         corpus=req.corpus, document_ids=req.document_ids or None,
                                         document_type=req.document_type)
        result["latency_ms"] = round((time.perf_counter() - started) * 1000, 2)
        return result
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(503, detail={"status": "RETRIEVAL_ERROR",
                         "message": rag.mask_secrets(f"{type(exc).__name__}: {exc}")[:500]})


class Citation(BaseModel):
    source_id: str | None = None
    n: int | None = None
    prompt_n: int | None = None
    doc_id: str
    title: str
    chunk_id: str
    chunk_ids: list[str] = Field(default_factory=list)
    breadcrumb: str | None = None
    page: int | None = None
    url: str | None = None
    snippet: str = ""
    score: float | None = None
    rerank_score: float | None = None
    query_coverage: float | None = None
    metadata_coverage: float | None = None
    section: str | None = None
    file_name: str | None = None
    retrieval_methods: list[str] = Field(default_factory=list)
    retrieval_scores: dict = Field(default_factory=dict)
    graph_paths: list[dict] = Field(default_factory=list)


class QueryResp(BaseModel):
    answer: str
    source: str
    corpus: str | None = None
    retrieval_mode: str = "graph"
    confidence_score: float | None = None
    confidence_method: str = ""
    latency_ms: float = 0.0
    evaluation_run_id: str = ""
    matched_question: dict | None = None
    citations: list[Citation]
    entities: list[dict] = []
    related_documents: list[dict] = []
    answer_mode: str = "llm"
    extractive_answer: str | None = None
    graph: dict = {"nodes": [], "edges": []}
    evidence: list[dict] = Field(default_factory=list)
    plan: dict = Field(default_factory=dict)
    context_doc_ids: list[str] = Field(default_factory=list)
    retrieval: dict = Field(default_factory=dict)
    timings_ms: dict = Field(default_factory=dict)
    validation: dict = Field(default_factory=dict)
    status: str = ""
    generation: dict = Field(default_factory=dict)
    debug: dict | None = None


@app.get("/kb/health")
def health():
    try:
        db = get_db()
        counts = {r["l"]: r["n"] for r in db.read("MATCH (n) UNWIND labels(n) AS l RETURN l, count(*) AS n")}
        try:
            apoc = db.read("RETURN apoc.version() AS v")[0]["v"]
        except Exception:
            apoc = None
        idx = [r["name"] for r in db.read("SHOW INDEXES YIELD name, state WHERE state = 'ONLINE' RETURN name")]
        embedded = db.read("MATCH (c:Chunk) WHERE c.embedding IS NOT NULL RETURN count(c) AS n")[0]["n"]
        notetaker_rows = db.read("""
            MATCH (d:Document {corpus:'notetaker'})
            OPTIONAL MATCH (d)-[:CONTAINS_CHUNK]->(c:Chunk)
            RETURN d.doc_id AS document_id, d.ingest_status AS ingest_status,
                   count(DISTINCT c.chunk_id) AS chunks,
                   count(DISTINCT CASE WHEN c.embedding IS NOT NULL THEN c.chunk_id END) AS embedded_chunks
        """)
        return {"status": "ok", "neo4j": "connected", "apoc": apoc, "llm": f"groq:{S.groq_model}" if rag.available() else "nonaktif", "vector_rag": {"configured": S.embeddings, "index_online": "chunk_embedding" in idx, "embedded_chunks": embedded}, "corpora": {"notetaker": {"documents": notetaker_rows}}, "nodes": counts, "indexes_online": idx}
    except Exception as e:
        raise HTTPException(503, f"neo4j tidak tersedia: {e}")


def _graph(cites: list[dict], ents: list[dict]) -> dict:
    nodes, edges = {}, []

    def n(i, label, kind):
        nodes.setdefault(i, {"id": i, "label": label[:60], "type": kind})

    def e(a, b, rel):
        edges.append({"source": a, "target": b, "rel": rel})
    for c in cites:
        n(c["chunk_id"], (c.get("breadcrumb") or c["chunk_id"]).split(" > ")[-1], "Chunk")
        n(c["doc_id"], c["title"], "Document"); e(c["doc_id"], c["chunk_id"], "CONTAINS_CHUNK")
    for x in ents:
        if x["doc_id"] not in nodes:
            continue
        for key, kind, rel in (("unit", "UnitKerja", "PRODUCED_BY"), ("division", "UnitKerja", "UNDER_DIVISION"), ("category", "Category", "IN_CATEGORY")):
            if x.get(key):
                n(f"{kind}:{x[key]}", x[key], kind); e(x["doc_id"], f"{kind}:{x[key]}", rel)
        for t in x["tags"]:
            n(f"Tag:{t}", t, "Tag"); e(x["doc_id"], f"Tag:{t}", "TAGGED_WITH")
    return {"nodes": list(nodes.values()), "edges": edges}


def _record_query(db: DB, record: dict) -> None:
    try:
        S.reports_dir.mkdir(parents=True, exist_ok=True)
        log_path = S.reports_dir / "query_runs.jsonl"
        line = json.dumps(record, ensure_ascii=False, default=str)
        with _query_log_lock, log_path.open("a", encoding="utf-8") as log_file:
            log_file.write(line + "\n")
    except Exception as exc:
        print(f"[warn] Gagal mencatat query ke JSONL: {exc}", flush=True)


NOT_FOUND_TEXT = "Informasi tersebut belum ditemukan dalam sumber yang diperiksa."
EMPTY_CONTEXT_TEXT = "Tidak ada chunk yang dapat dijadikan konteks untuk pertanyaan ini, sehingga LLM tidak dipanggil."
LLM_FAIL_TEXT = ("Jawaban belum dapat dibuat karena kegagalan teknis pada layanan LLM (kategori: {cat}"
                 "{http}). Ini bukan berarti informasi tidak ada pada dokumen; silakan coba lagi.")


@app.post("/kb/query", response_model=QueryResp)
def query(req: QueryReq):
    started = time.perf_counter()
    db = get_db()
    # ---- 1. Retrieval (kegagalan dilaporkan sebagai RETRIEVAL_ERROR, bukan "tidak ditemukan") ----
    try:
        if req.mode == "vector":
            res = retrieval.answer_vector_only(db, req.question, req.top_k, corpus=req.corpus,
                                               document_id=req.document_id, context_doc_ids=req.context_doc_ids)
            ents, rel = [], []
        else:
            res = retrieval.answer(db, req.question, req.top_k, corpus=req.corpus,
                                   document_id=req.document_id, context_doc_ids=req.context_doc_ids,
                                   neighbor_window=req.neighbor_window)
            ids = list(dict.fromkeys(c["doc_id"] for c in res["citations"]))
            ents = search.doc_entities(db, ids) if ids else []
            want_related = "terkait" in res.get("plan", {}).get("intents", [])
            rel = search.related_docs(db, ids[0], 5, req.corpus) if ids and want_related else []
    except Exception as e:  # noqa: BLE001
        print(f"RETRIEVAL ERROR:\n{traceback.format_exc()}", flush=True)
        raise HTTPException(503, detail={"status": "RETRIEVAL_ERROR", "message": rag.mask_secrets(f"{type(e).__name__}: {e}")[:500]})
    retrieval_ms = round((time.perf_counter() - started) * 1000, 2)
    candidates = list(res.get("evidence", []))          # chunk hasil retrieval + ranking (sebelum seleksi konteks)
    candidate_citations = list(res.get("citations", []))

    # ---- 2. Generasi: SATU panggilan Groq; prompt final dicatat dari objek yang sama ----
    gen_started = time.perf_counter()
    gen = rag.generate(req.question, candidates, max_context_chars=req.context_chars)
    generation_ms = round((time.perf_counter() - gen_started) * 1000, 2)
    sent = gen["context_sent"]
    validation: dict = {}
    citations: list[dict] = []
    citation_map: dict = {}
    raw_answer = gen.get("answer")

    if gen["status"] == "skipped_no_evidence":
        status, answer, answer_mode = "EMPTY_CONTEXT", EMPTY_CONTEXT_TEXT, "no_evidence"
    elif gen["status"] == "disabled":
        status, answer, answer_mode = "LLM_ERROR", "Generasi LLM dinonaktifkan (USE_LLM/GROQ_API_KEY).", "llm_disabled"
    elif gen["status"] == "failed":
        status, answer, answer_mode = gen["eval_status"], LLM_FAIL_TEXT.format(
            cat=gen["error_category"], http=f", HTTP {gen['http_status']}" if gen.get("http_status") else ""), "llm_failed"
    else:
        validation = rag.validate_answer(raw_answer, sent)
        status = rag.eval_status_for(raw_answer, validation)
        answer, citations, citation_map = rag.finalize_citations(raw_answer, sent)
        answer_mode = "llm"
        if status == "NOT_FOUND" and not answer.strip():
            answer = NOT_FOUND_TEXT

    validation.update({
        "citation_structure": ("passed" if citations and not validation.get("invalid_markers") else
                               "invalid_markers" if validation.get("invalid_markers") else "no_cited_claims"),
        "generation": {"generated": "generated", "failed": "llm_failed"}.get(gen["status"], gen["status"]),
        "answer_relevance": "not_automatically_checked",
    })
    confidence, confidence_method = (rag.assess_confidence(req.question, raw_answer, sent)
                                     if raw_answer and sent else (None, "answer_not_generated"))
    latency_ms = round((time.perf_counter() - started) * 1000, 2)
    run_id = str(uuid.uuid4())
    generation = {
        "status": gen["status"], "eval_status": status, "model": gen["model"], "attempts": gen["attempts"],
        "attempt_count": len(gen["attempts"]), "error_category": gen["error_category"],
        "error_message": gen["error_message"], "http_status": gen["http_status"],
        "context_chunks_sent": len(sent), "context_chars_sent": (gen.get("prompt") or {}).get("context_chars", 0),
        "llm_calls_made": len(gen["attempts"]),
    }
    res.update(answer=answer, answer_mode=answer_mode, extractive_answer=None, citations=citations,
               evidence=sent, status=status, generation=generation, validation=validation,
               corpus=req.corpus, retrieval_mode=req.mode, confidence_score=confidence,
               confidence_method=confidence_method, latency_ms=latency_ms, evaluation_run_id=run_id,
               entities=ents, related_documents=rel,
               graph=_graph(citations, ents) if req.mode == "graph" and req.include_graph else {"nodes": [], "edges": []})
    res["retrieval"] = {
        "vector_results": sum("vector" in c.get("retrieval_methods", []) for c in candidate_citations),
        "graph_results": sum(any(m.startswith("graph") for m in c.get("retrieval_methods", [])) for c in candidate_citations),
        "selected_chunks": len(sent), "candidate_count": len(candidate_citations),
        "candidate_chunks": [{"rank": rank, "chunk_id": c.get("chunk_id"), "doc_id": c.get("doc_id"),
                              "file_name": c.get("file_name"), "score": c.get("score"),
                              "retrieval_methods": c.get("retrieval_methods"), "snippet": c.get("snippet")}
                             for rank, c in enumerate(candidate_citations, start=1)],
        "llm_generation_attempted": gen["status"] in ("generated", "failed"),
        "context_chunk_ids": [e.get("chunk_id") for e in sent],
    }
    res["timings_ms"] = {"retrieval": retrieval_ms, "generation": generation_ms,
                         "total": round((time.perf_counter() - started) * 1000, 2)}
    # Snapshot tahap-tahap pipeline. Disimpan selalu di log; dikirim ke klien bila debug=true.
    debug_info = {
        "question": req.question, "retrieval_mode": req.mode, "retrieval_trace": res.get("plan", {}).get("trace", []),
        "stage_1_retrieved_chunks": [{"chunk_id": c.get("chunk_id"), "doc_id": c.get("doc_id"), "score": c.get("score"),
                                      "methods": c.get("retrieval_methods")} for c in candidate_citations],
        "stage_2_chunks_selected_for_context": [e.get("chunk_id") for e in sent],
        "stage_3_4_final_prompt_sent_to_llm": gen.get("prompt"),   # system/user prompt + konteks final (kredensial disamarkan)
        "context_sent_to_llm": [{"n": e["n"], "orig_n": e.get("orig_n"), "chunk_id": e.get("chunk_id"), "doc_id": e.get("doc_id"),
                                 "file_name": e.get("file_name"), "title": e.get("title"), "section": e.get("section"),
                                 "retrieval_methods": e.get("retrieval_methods"), "retrieval_scores": e.get("retrieval_scores"),
                                 "text": e.get("text"), "neighbors": e.get("neighbors", [])} for e in sent],
        "stage_5_llm_raw_answer": raw_answer, "stage_6_final_answer": answer, "citation_map_prompt_to_final": citation_map,
        "generation": generation, "timings_ms": res["timings_ms"],
    }
    res["debug"] = debug_info if req.debug else None
    _record_query(db, {
        "run_id": run_id, "created_at": datetime.now(timezone.utc).isoformat(), "question": req.question,
        "answer": answer, "status": status, "corpus": req.corpus, "mode": req.mode, "answer_mode": answer_mode,
        "confidence_score": confidence, "confidence_method": confidence_method, "latency_ms": latency_ms,
        "citations": citations, "retrieval": res["retrieval"], "validation": validation,
        "selected_chunk_ids": [c.get("chunk_id") for c in citations], "debug": debug_info,
        "timings_ms": res["timings_ms"],
    })
    return res


@app.get("/")
def root():
    return {"service": "ARCANA KB API", "docs": "/docs", "health": "/kb/health"}