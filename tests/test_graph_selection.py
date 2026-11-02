"""Uji offline (tanpa Neo4j/Groq) untuk perbaikan hasil audit Graph RAG."""
from kb import search
from kb.config import S


def _row(i, doc="NT-001", methods=("fulltext",), rrf=1.0, cov=0.8, text=None):
    return {"chunk_id": f"{doc}_c{i}", "doc_id": doc, "text": text or f"isi unik {doc} {i}", "rrf": rrf,
            "retrieval_methods": list(methods), "cov": cov, "section": "transcript"}


def test_fills_top_k_for_single_document():
    """Regresi: batas lama per_doc>=3 hanya memberi 3 chunk walau kandidat banyak."""
    fused = [_row(i, rrf=1 - i / 100) for i in range(20)]
    best, st = search.select_top(fused, 5)
    assert len(best) == 5 and "backfill_to_top_k" in st


def test_diversity_pass_prefers_other_docs_before_backfill():
    fused = [_row(i, "NT-001", rrf=1 - i / 100) for i in range(6)] + [_row(0, "NT-002", rrf=0.2)]
    best, _ = search.select_top(fused, 5)
    assert "NT-002" in {r["doc_id"] for r in best}
    assert len(best) == 5


def test_graph_only_low_coverage_dropped_but_not_if_all_would_vanish():
    good = _row(1, rrf=1.0)
    bad = _row(2, "DOC-9", ("graph_entity_document_chunks",), rrf=0.9, cov=0.0)
    best, st = search.select_top([good, bad], 5)
    assert [r["chunk_id"] for r in best] == [good["chunk_id"]]
    only_bad, _ = search.select_top([bad], 5)
    assert len(only_bad) == 1


def test_duplicate_text_removed():
    a, b = _row(1, text="Teks   sama."), _row(2, text="teks sama.")
    best, st = search.select_top([a, b], 5)
    assert len(best) == 1


def test_rrf_weights_downweight_entity_list():
    a = [{"chunk_id": "x", "doc_id": "d", "text": "t"}]
    out = search.rrf([a, a], methods=["fulltext", "graph_entity_document_chunks"], weights=[1.0, 0.5])
    assert abs(out[0]["rrf"] - 1.5 / 61) < 1e-9


def test_cypher_has_corpus_filter():
    assert "$corpus" in search.CHUNK_LEXICAL
    import inspect
    assert "$corpus" in inspect.getsource(search.expand_graph)
    assert "$corpus" in inspect.getsource(search.entity_docs)


def test_config_defaults_keep_model():
    assert S.groq_model == "openai/gpt-oss-120b"
