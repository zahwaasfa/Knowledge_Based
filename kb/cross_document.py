"""Independent cross-document retrieval orchestration over the shared KB search layer.

The module does not assume a corpus, golden set, session, or document ID. Optional
filters are applied only when explicitly supplied by the caller.
"""
from __future__ import annotations

from . import search
from .query_plan import analyze


def retrieve(db, question: str, top_k: int = 8, *, corpus: str | None = None,
             document_ids: list[str] | None = None, document_type: str | None = None) -> dict:
    """Return deduplicated evidence from multiple documents plus graph-link trace.

    Uses the same chunk search/ranking implementation as GraphRAG. Linked documents
    are expanded through the existing entity/tag graph and searched using that same
    implementation, avoiding a second retrieval algorithm.
    """
    plan = analyze(question)
    initial, stages = search.search_chunks(db, plan, max(top_k, 1), document_ids,
                                          corpus=corpus, restrict_doc_ids=bool(document_ids))
    initial_doc_ids = list(dict.fromkeys(hit["doc_id"] for hit in initial))
    linked = search.expand_graph(db, initial_doc_ids, limit=max(top_k * 2, 8), corpus=corpus)
    linked_ids = list(dict.fromkeys(row["doc_id"] for row in linked))
    linked_ids = [doc_id for doc_id in linked_ids if doc_id not in initial_doc_ids]
    expanded, expanded_stages = (search.search_chunks(db, plan, max(top_k, 1), linked_ids,
                                                       corpus=corpus, restrict_doc_ids=True)
                                 if linked_ids else ([], []))
    for hit in initial + expanded:
        hit.setdefault("retrieval_methods", ["graph_search"])
    # Deduplicate by chunk while preserving the highest-ranked occurrence.
    unique: dict[str, dict] = {}
    for hit in initial + expanded:
        key = str(hit.get("chunk_id") or "")
        if key and key not in unique:
            unique[key] = hit
    evidence = list(unique.values())[:top_k]
    docs = list(dict.fromkeys(hit["doc_id"] for hit in evidence))
    if document_type:
        # The current graph schema has no normalized document_type filter. Report
        # this clearly instead of silently pretending the filter was enforced.
        filter_status = "unsupported_by_current_schema"
    else:
        filter_status = "not_requested"
    return {
        "question": question,
        "retrieval_mode": "cross_document_graph",
        "source_documents": [{"doc_id": doc_id, "title": next((h.get("title") for h in evidence if h.get("doc_id") == doc_id), None)}
                             for doc_id in docs],
        "document_ids": docs,
        "evidence": evidence,
        "citations": [{"doc_id": h.get("doc_id"), "title": h.get("title"),
                       "chunk_id": h.get("chunk_id"), "page": h.get("page"),
                       "file_name": h.get("file_name"), "snippet": (h.get("text") or "")[:500],
                       "score": h.get("score"), "source_id": f"S{i}"}
                      for i, h in enumerate(evidence, 1)],
        "graph_links": linked,
        "trace": stages + [f"cross_document_links={len(linked)}"] + expanded_stages,
        "filters": {"corpus": corpus, "document_ids": document_ids or [],
                    "document_type": document_type, "document_type_status": filter_status},
        "status": "ok" if evidence else "no_evidence",
    }
