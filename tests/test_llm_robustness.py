"""Uji komponen generasi LLM dengan mock: timeout, rate limit, konteks kosong, sitasi tidak valid, snapshot prompt.
Tidak ada request jaringan."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pytest
from kb import rag


class Err(Exception):
    def __init__(self, msg, status_code=None, headers=None):
        super().__init__(msg)
        self.status_code = status_code
        self.response = type("R", (), {"headers": headers or {}})()


class FakeLLM:
    def __init__(self, *outcomes):
        self.outcomes, self.calls, self.last_messages = list(outcomes), 0, None

    def invoke(self, messages):
        self.calls += 1
        self.last_messages = messages
        out = self.outcomes.pop(0)
        if isinstance(out, Exception):
            raise out
        return out


EVID = [
    {"n": 1, "chunk_id": "c1", "doc_id": "d1", "title": "Rapat A", "text": "Pedoman AI disusun karena pegawai sudah memakai AI."},
    {"n": 2, "chunk_id": "c2", "doc_id": "d1", "title": "Rapat A", "text": "Rapat berlangsung pada 18 Agustus 2026."},
]
Q = "Mengapa pedoman AI disusun?"
nosleep = lambda s: None


def test_timeout_is_retried_then_reported_as_LLM_TIMEOUT_not_not_found():
    llm = FakeLLM(Err("Request timed out."), Err("Request timed out."), Err("Request timed out."))
    r = rag.generate(Q, EVID, llm=llm, sleep=nosleep)
    assert llm.calls == 3 and r["status"] == "failed" and r["eval_status"] == "LLM_TIMEOUT"
    assert r["answer"] is None


def test_rate_limit_with_long_retry_after_fails_fast_without_retry():
    llm = FakeLLM(Err("rate limit", 429, {"retry-after": "3600"}), Err("x"))
    r = rag.generate(Q, EVID, llm=llm, sleep=nosleep)
    assert llm.calls == 1 and r["eval_status"] == "LLM_RATE_LIMIT" and r["attempts"][0]["retry_after"] == 3600


def test_rate_limit_short_retry_after_is_retried_and_succeeds():
    llm = FakeLLM(Err("rate limit", 429, {"retry-after": "1"}), "Karena pegawai sudah memakai AI. [1]")
    r = rag.generate(Q, EVID, llm=llm, sleep=nosleep)
    assert llm.calls == 2 and r["status"] == "generated"


def test_bad_request_is_not_retried():
    llm = FakeLLM(Err("invalid", 400), "tidak dipakai")
    r = rag.generate(Q, EVID, llm=llm, sleep=nosleep)
    assert llm.calls == 1 and r["eval_status"] == "LLM_ERROR" and r["error_category"] == "bad_request"


def test_request_too_large_retries_once_with_fewer_chunks():
    llm = FakeLLM(Err("Request too large", 413), "Karena pegawai sudah memakai AI. [1]")
    r = rag.generate(Q, EVID, llm=llm, sleep=nosleep)
    assert r["status"] == "generated" and len(r["context_sent"]) == 1


def test_empty_evidence_never_calls_llm():
    llm = FakeLLM("x")
    r = rag.generate(Q, [], llm=llm, sleep=nosleep)
    assert llm.calls == 0 and r["status"] == "skipped_no_evidence"


def test_snapshot_prompt_is_the_exact_prompt_sent_to_llm():
    llm = FakeLLM("Karena pegawai sudah memakai AI. [1]")
    r = rag.generate(Q, EVID, llm=llm, sleep=nosleep)
    sent_user = llm.last_messages[1].content
    assert r["prompt"]["user_prompt"] == sent_user
    assert "Pedoman AI disusun karena pegawai" in r["prompt"]["context_text"]
    assert [c["chunk_id"] for c in r["prompt"]["chunks"]] == [e["chunk_id"] for e in r["context_sent"]]


def test_unknown_citation_number_is_invalid_and_stripped():
    sent = rag.build_prompt(Q, EVID).evidence
    ans = "Karena pegawai sudah memakai AI tanpa panduan. [1] Ini klaim lain yang dikarang. [7]"
    v = rag.validate_answer(ans, sent)
    assert v["invalid_markers"] == [7] and rag.eval_status_for(ans, v) == "INVALID_CITATION"
    text, cites, mapping = rag.finalize_citations(ans, sent)
    assert "[7]" not in text and [c["chunk_id"] for c in cites] == ["c1"]


def test_no_citation_is_never_fabricated():
    sent = rag.build_prompt(Q, EVID).evidence
    ans = "Pedoman disusun karena pegawai sudah memakai AI."
    text, cites, _ = rag.finalize_citations(ans, sent)
    assert cites == [] and "[" not in text
    assert rag.eval_status_for(ans, rag.validate_answer(ans, sent)) == "INVALID_CITATION"


def test_not_found_statement_status_and_partial():
    sent = rag.build_prompt(Q, EVID).evidence
    nf = "Informasi tersebut belum ditemukan dalam sumber yang diperiksa."
    assert rag.eval_status_for(nf, rag.validate_answer(nf, sent)) == "NOT_FOUND"
    part = "Pegawai sudah memakai AI untuk tugas kedinasan. [1] Tanggal pengesahan belum ditemukan dalam sumber."
    assert rag.eval_status_for(part, rag.validate_answer(part, sent)) == "PARTIAL"


def test_unsupported_claim_and_number_detected():
    sent = rag.build_prompt(Q, EVID).evidence
    ans = "Rapat menyepakati anggaran sebesar 500 miliar rupiah untuk server baru. [2]"
    v = rag.validate_answer(ans, sent)
    assert v["unsupported_claims"] == 1 and rag.eval_status_for(ans, v) == "UNSUPPORTED_ANSWER"


def test_supported_answer_is_ANSWERED_and_renumbered_contiguously():
    sent = rag.build_prompt(Q, EVID).evidence
    ans = "Rapat berlangsung pada 18 Agustus 2026. [2]"
    v = rag.validate_answer(ans, sent)
    assert rag.eval_status_for(ans, v) == "ANSWERED"
    text, cites, mapping = rag.finalize_citations(ans, sent)
    assert text.endswith("[1]") and cites[0]["chunk_id"] == "c2" and mapping == {"2": 1}


def test_classify_parses_retry_after_from_groq_message():
    f = rag.classify_exception(Err("Rate limit reached ... Please try again in 7.5s.", 429))
    assert f.category == "rate_limit" and f.retry_after == 7.5
    assert rag.mask_secrets("key gsk_abcdefghij1234567890") == "key gsk_***"
