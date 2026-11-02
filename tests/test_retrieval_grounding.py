from types import SimpleNamespace
from kb import extract, rag, retrieval, search
from kb.query_plan import analyze


def test_rrf_deduplicates_by_chunk_and_keeps_retrieval_provenance():
    ft = [{"chunk_id": "c1", "doc_id": "d1", "score": 7.5},
          {"chunk_id": "c2", "doc_id": "d2", "score": 6.0}]
    vector = [{"chunk_id": "c1", "doc_id": "d1", "score": 0.91}]

    fused = search.rrf([ft, vector], methods=["fulltext", "vector"])

    assert [row["chunk_id"] for row in fused].count("c1") == 1
    c1 = next(row for row in fused if row["chunk_id"] == "c1")
    assert set(c1["retrieval_methods"]) == {"fulltext", "vector"}
    assert c1["retrieval_scores"] == {"fulltext": 7.5, "vector": 0.91}
    assert c1["rrf"] == (1 / 61) + (1 / 61)


def test_rag_validation_rejects_unknown_or_missing_citations():
    evidence = [{"n": 1, "chunk_id": "c1", "text": "Bukti."}]

    assert rag.valid("Klaim didukung. [1]", evidence)
    assert not rag.valid("Klaim didukung. [2]", evidence)
    assert not rag.valid("Klaim tanpa sitasi.", evidence)
    assert rag.valid("Informasi belum ditemukan dalam bukti yang tersedia.", evidence)


def test_rag_validation_requires_citation_for_each_factual_sentence():
    evidence = [{"n": 1, "chunk_id": "c1", "text": "Bukti."}]
    assert rag.valid("**Rencana utama:**\nHub akan menjadi repositori pengetahuan terpadu. [1]", evidence)
    assert rag.valid("Rencana utama sudah disetujui. [1] Tanggalnya awal bulan. [1]", evidence)
    assert not rag.valid("Rencana utama sudah disetujui. [1] Tanggalnya awal bulan.", evidence)


def test_context_reranker_promotes_chunks_matching_question():
    evidence = [
        {"n": 1, "title": "Dokumen lain", "text": "Topik lain dan pembahasan umum."},
        {"n": 2, "title": "Makrointelligence Hub", "text": "Rencana membangun repositori pengetahuan berbasis RAG."},
    ]
    selected = rag.select_context(evidence, question="Apa rencana Makrointelligence Hub?", max_chunks=2)
    assert selected[0]["n"] == 2


def test_explicit_acronym_filters_when_some_hits_match_and_keeps_hits_otherwise():
    hits = [
        {"doc_id": "d1", "title": "Rapat UGM", "text": "Bappenas membahas rencana."},
        {"doc_id": "d2", "title": "Ekonomi Indonesia", "text": "Laporan ekonomi."},
    ]
    selected = retrieval._filter_named_anchors("Apa rencana Bappenas di UGM?", hits)
    assert [hit["doc_id"] for hit in selected] == ["d1"]
    # Bila tidak ada hit yang memuat jangkar, hasil dipertahankan; LLM yang menilai relevansi (aturan prompt no. 7).
    assert retrieval._filter_named_anchors("Apa agenda UGM?", [hits[1]]) == [hits[1]]


def test_graph_chunk_candidates_keep_the_relationship_path(monkeypatch):
    class FakeDB:
        def read(self, query, **params):
            return [{"chunk_id": f"{doc_id}_chunk", "doc_id": doc_id, "text": "Pusdatin mengelola infrastruktur."}
                    for doc_id in params["ids"]]

    monkeypatch.setattr(search, "entity_docs", lambda *args, **kwargs: [
        {"doc_id": "d1", "kind": "Organization", "entity": "Pusdatin", "rel": "BELONGS_TO_ORG", "role": "penyusun"}
    ])
    calls = []
    def expand(db, doc_ids, **kwargs):
        calls.append(kwargs)
        return [{"doc_id": "d2", "hops": 1, "via": "kemiripan_chunk", "shared": [{"name": "Pusdatin"}]}]
    monkeypatch.setattr(search, "expand_graph", expand)
    hits = search._graph_chunk_hits(FakeDB(), SimpleNamespace(topic=["Pusdatin"]), 3, "notetaker")
    assert hits[0]["retrieval_methods"] == ["graph_entity_document_chunks"]
    assert hits[0]["graph_paths"][0]["relationship"] == "BELONGS_TO_ORG"
    neighbor = next(hit for hit in hits if hit["doc_id"] == "d2")
    assert neighbor["graph_paths"][0]["hops"] == 1
    assert calls[0]["two_hop"] is False


def test_markdown_transcript_turn_is_an_atomic_timestamped_block():
    blocks = extract.text_to_blocks("# Transcript\n\n**Narasumber** (01:23): Rapat menyepakati tindak lanjut.")
    turn = blocks[-1]
    assert turn["atomic"] is True
    assert turn["section"] == "transcript"
    assert turn["text"] == "[01:23] Narasumber: Rapat menyepakati tindak lanjut."


def test_context_budget_keeps_only_whole_chunks():
    evidence = [{"n": 1, "text": "a" * 100}, {"n": 2, "text": "b" * 100}]

    selected = rag.select_context(evidence, max_chars=350)

    assert selected == evidence[:1]


def test_vector_reranker_uses_content_metadata_and_preserves_cosine_score():
    hits = [
        {"chunk_id": "noise", "doc_id": "d2", "title": "Indeks Perencanaan", "file_name": "other.md",
         "text": "Indeks pembangunan dan metodologi umum.", "score": 0.94},
        {"chunk_id": "meeting", "doc_id": "d1", "title": "Pembahasan Masukan Akademisi Pedoman AI",
         "file_name": "20260818-rapat-pedoman-ai.md",
         "text": "Konsultasi akademisi membahas draf pedoman pemanfaatan AI Bappenas.", "score": 0.82},
    ]
    ranked = search.rerank_vector_hits(
        "Dalam konsultasi akademisi untuk draf Pedoman AI Bappenas pada 18 Agustus 2026, apa topik utama?", hits
    )
    assert ranked[0]["chunk_id"] == "meeting"
    assert ranked[0]["score"] == 0.82  # original cosine similarity remains available
    assert ranked[0]["date_match"] is True
    assert search._query_date_key("18 Agustus 2026") == "20260818"


def test_graph_document_resolution_searches_transcript_chunks_before_catalog_sections(monkeypatch):
    doc = {"doc_id": "NT-001", "title": "Pembahasan Masukan Akademisi untuk Pedoman AI",
           "file_name": "20260818-pedoman-ai.md", "cover": 1.0, "rank": 0.9}
    hit = {"doc_id": "NT-001", "title": doc["title"], "chunk_id": "NT-001-C42",
           "text": "Konsultasi membahas penyusunan draf pedoman pemanfaatan AI.",
           "section": "transcript", "file_name": doc["file_name"],
           "retrieval_methods": ["fulltext"], "retrieval_scores": {"fulltext": 1.2}, "rank": 0.9}
    monkeypatch.setattr(search, "find_documents", lambda *args, **kwargs: ([doc], ["document_ft"]))
    monkeypatch.setattr(search, "search_chunks", lambda *args, **kwargs: ([hit], ["chunk_ft"]))
    monkeypatch.setattr(search, "section_chunks", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("catalog sections should not replace transcript chunks")))

    result = retrieval.answer(object(), "Apa topik utama konsultasi akademisi untuk draf Pedoman AI?", corpus=None)

    assert result["source"] == "graph_chunks"
    assert result["answer"] == ""          # retrieval tidak pernah memanggil LLM / tidak ada jawaban dari teks mentah
    assert "draf pedoman pemanfaatan AI" in result["evidence"][0]["text"]
    assert result["citations"][0]["chunk_id"] == "NT-001-C42"
    assert result["evidence"][0]["section"] == "transcript"
