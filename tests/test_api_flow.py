"""Alur API end-to-end dengan retrieval & LLM di-mock: satu panggilan LLM per query, konteks aktual = prompt final, status eksplisit."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from fastapi.testclient import TestClient
from kb import rag, retrieval, search
from kb_api import main

EV = [{"n": 1, "chunk_id": "c1", "doc_id": "d1", "title": "Rapat A", "section": "transcript", "file_name": "a.md",
       "text": "Pedoman AI disusun karena pegawai sudah memakai AI.", "score": 0.9, "retrieval_methods": ["fulltext"],
       "retrieval_scores": {"fulltext": 0.9}, "graph_paths": []}]


def _setup(monkeypatch, evidence, llm_outcomes):
    calls = {"n": 0, "messages": None}
    monkeypatch.setattr(main, "get_db", lambda: object())
    monkeypatch.setattr(main, "_record_query", lambda *a, **k: None)
    monkeypatch.setattr(search, "doc_entities", lambda *a, **k: [])
    cites = [{k: v for k, v in e.items() if k != "text"} | {"snippet": e["text"]} for e in evidence]
    monkeypatch.setattr(retrieval, "answer", lambda *a, **k: {"answer": "", "source": "graph_chunks", "citations": cites,
                                                              "evidence": [dict(e) for e in evidence], "plan": {"trace": []}})
    monkeypatch.setattr(rag, "available", lambda: True)

    def fake_invoke(llm, payload, max_tokens):
        calls["n"] += 1
        calls["messages"] = payload.user
        out = llm_outcomes.pop(0)
        if isinstance(out, Exception):
            raise out
        return out, "stop"
    monkeypatch.setattr(rag, "_invoke", fake_invoke)
    return calls


def _post(**kw):
    return TestClient(main.app).post("/kb/query", json={"question": "Mengapa pedoman AI disusun?", "mode": "graph", "debug": True, **kw})


def test_single_llm_call_actual_context_and_citations(monkeypatch):
    calls = _setup(monkeypatch, EV, ["Karena pegawai sudah memakai AI. [1]"])
    r = _post().json()
    assert calls["n"] == 1                                    # tidak ada panggilan ganda
    assert r["status"] == "ANSWERED" and r["answer_mode"] == "llm"
    assert r["debug"]["stage_3_4_final_prompt_sent_to_llm"]["user_prompt"] == calls["messages"]
    assert r["debug"]["context_sent_to_llm"][0]["text"] == EV[0]["text"]
    assert r["citations"][0]["chunk_id"] == "c1" and r["answer"].endswith("[1]")


def test_provider_failure_is_not_reported_as_not_found(monkeypatch):
    class E(Exception):
        status_code = 429
    monkeypatch.setattr(rag, "time", type("T", (), {"perf_counter": staticmethod(__import__("time").perf_counter)}))
    monkeypatch.setattr(rag.random, "uniform", lambda a, b: 0)
    calls = _setup(monkeypatch, EV, [E("rate limit"), E("rate limit"), E("rate limit")])
    r = _post().json()
    assert r["status"] == "LLM_RATE_LIMIT" and r["answer_mode"] == "llm_failed"
    assert "belum ditemukan" not in r["answer"] and r["citations"] == []
    assert "Pedoman AI disusun" not in r["answer"]            # tidak ada fallback teks mentah chunk


def test_empty_retrieval_gives_EMPTY_CONTEXT_without_llm_call(monkeypatch):
    calls = _setup(monkeypatch, [], [])
    r = _post().json()
    assert calls["n"] == 0 and r["status"] == "EMPTY_CONTEXT"
