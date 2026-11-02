"""Run real ARCANA RAG evaluations, preserve raw evidence, and export an Excel copy."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from kb.config import S  # noqa: E402


def norm_file(value: str | None) -> str:
    """Normalize only path separators/case; expected source matching is basename exact."""
    value = (value or "").replace("\\", "/").rstrip("/")
    return value.rsplit("/", 1)[-1].casefold()


def post_json(url: str, payload: dict, timeout: int = 300) -> tuple[dict, float]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:  # sertakan isi error terstruktur (mis. RETRIEVAL_ERROR) dari API
        detail = exc.read().decode("utf-8", "replace")[:800]
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc
    return json.loads(body), (time.perf_counter() - started) * 1000


def get_json(url: str, timeout: int = 10) -> dict:
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def context_to_text(context: list[dict] | None) -> str:
    if not context:
        return ""
    blocks = []
    for index, item in enumerate(context, start=1):
        marker = item.get("n", index)
        metadata = [
            f"Chunk ID: {item.get('chunk_id') or 'tidak tersedia'}",
            f"Document ID: {item.get('doc_id') or 'tidak tersedia'}",
            f"File: {item.get('file_name') or 'tidak tersedia'}",
            f"Judul: {item.get('title') or 'tidak tersedia'}",
            f"Section: {item.get('section') or 'tidak tersedia'}",
            f"Metode: {', '.join(item.get('retrieval_methods') or []) or 'tidak tersedia'}",
        ]
        body = item.get("text") or ""
        for nb in item.get("neighbors") or []:
            tag = "percakapan sebelumnya" if nb.get("position") == "before" else "percakapan berikutnya"
            body += f"\n({tag}, chunk {nb.get('chunk_id')}) {nb.get('text') or ''}"
        blocks.append(f"[{marker}]\n" + "\n".join(metadata) + f"\nIsi chunk (termasuk tetangga yang dikirim ke LLM):\n{body}")
    return "\n\n".join(blocks)


def citations_valid(answer: str, citations: list[dict]) -> bool | None:
    """Struktur: setiap [n] harus menunjuk sitasi yang ada dan memiliki chunk_id/doc_id."""
    markers = re.findall(r"\[(?:S)?(\d+)\]", answer or "")
    if not markers:
        return None
    for marker in markers:
        index = int(marker) - 1
        if index < 0 or index >= len(citations):
            return False
        item = citations[index]
        if not item.get("chunk_id") or not item.get("doc_id"):
            return False
    return True


def citation_markers(answer: str) -> list[str]:
    return list(dict.fromkeys(f"[{m}]" for m in re.findall(r"\[(?:S)?(\d+)\]", answer or "")))


def proxy_metrics(candidates: list[dict], expected_files: list[str], top_k: int) -> dict:
    """Document-name proxy for raw document matching only; workbook Precision waits for chunk review."""
    expected = {norm_file(name) for name in expected_files if norm_file(name)}
    ranked = candidates[:top_k]
    found_by_rank = [norm_file(row.get("file_name")) in expected and bool(row.get("file_name")) for row in ranked]
    relevant_unique = {norm_file(row.get("file_name")) for row, hit in zip(ranked, found_by_rank) if hit}
    unique_retrieved = {norm_file(row.get("file_name")) for row in ranked if norm_file(row.get("file_name"))}
    first_rank = next((rank for rank, hit in enumerate(found_by_rank, 1) if hit), None)
    return {
        "precision_at_k_expected_file_proxy": (sum(found_by_rank) / len(ranked)) if ranked else None,
        "recall_at_k_expected_unique_file_proxy": (len(relevant_unique) / len(expected)) if expected else None,
        "mrr_expected_file_proxy": (1 / first_rank) if first_rank else 0.0,
        "hit_rate_at_k_expected_file_proxy": bool(first_rank),
        "retrieved_unique_files": sorted(unique_retrieved),
        "expected_unique_files": sorted(expected),
        "first_expected_file_rank": first_rank,
    }


def excel_output_path(path: Path) -> Path:
    return path.with_suffix(".xlsx")


def export_workbook(raw_results: Path, output: Path, append: bool = False, replace_existing_ids: bool = False) -> None:
    exporter = ROOT / "scripts" / "export_eval_workbook.py"
    command = [sys.executable, str(exporter), "--results", str(raw_results), "--output", str(output)]
    if append:
        command.append("--append")
    if replace_existing_ids:
        command.append("--replace-existing-ids")
    subprocess.run(command, check=True, cwd=ROOT)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api", default=S.api_url)
    parser.add_argument("--golden-set", default=str(ROOT / "evaluation" / "golden_set_notetaker_75.json"))
    parser.add_argument("--output", default=None, help="File JSON mentah; default memakai nama bertanggal.")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--mode", choices=["graph", "vector", "both"], default="both")
    parser.add_argument("--limit", type=int, default=None,
                        help="Batas smoke test pada N pertanyaan pertama; default menjalankan seluruh Golden Set.")
    parser.add_argument("--corpus", choices=["bappenas", "notetaker"], default=None,
                        help="Opsional; default mencari seluruh korpus aktif.")
    parser.add_argument("--workbook", default=None, help=argparse.SUPPRESS)
    parser.add_argument("--workbook-output", default=None, help="Path workbook hasil; default mengikuti nama JSON, atau workbook kumulatif saat --append-workbook.")
    parser.add_argument("--append-workbook", action="store_true", help="Pakai workbook kumulatif; default path reports/rag_evaluation_kumulatif.xlsx.")
    parser.add_argument("--replace-existing-ids", action="store_true", help="Ganti hasil detail lama untuk ID yang dijalankan ulang; ringkasan sesi lama tetap disimpan. Otomatis mengaktifkan append workbook.")
    parser.add_argument("--delay", type=float, default=2.0,
                        help="Jeda detik antar request (eksekusi sekuensial; melindungi kuota Groq/ARCANA).")
    parser.add_argument("--stop-after-llm-failures", type=int, default=5,
                        help="Hentikan run bila N kegagalan LLM berturut-turut (mis. kuota harian habis); sisa ditandai belum dijalankan.")
    parser.add_argument("--ids", default=None, help="Daftar ID pertanyaan dipisah koma (uji terbatas).")
    parser.add_argument("--no-excel", action="store_true", help="Simpan hasil JSON tanpa membuat workbook.")
    args = parser.parse_args()
    if args.replace_existing_ids:
        args.append_workbook = True

    golden_path = Path(args.golden_set)
    if not golden_path.is_file():
        print(f"Golden Set tidak ditemukan: {golden_path}", file=sys.stderr)
        return 2
    if args.top_k < 1 or args.top_k > 15:
        parser.error("--top-k harus antara 1 dan 15")

    golden = json.loads(golden_path.read_text(encoding="utf-8"))
    golden_total = len(golden)
    if args.ids:
        wanted = {x.strip() for x in args.ids.split(",") if x.strip()}
        golden = [g for g in golden if g["id"] in wanted]
        unknown = sorted(wanted - {g["id"] for g in golden})
        if unknown:
            print(f"ID tidak ditemukan di Golden Set: {', '.join(unknown)}", file=sys.stderr)
            return 2
        if not wanted:
            parser.error("--ids harus memuat minimal satu ID")
    if args.limit is not None:
        if args.limit < 1:
            parser.error("--limit minimal 1")
        golden = golden[:args.limit]
    modes = ["graph", "vector"] if args.mode == "both" else [args.mode]
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    output = Path(args.output) if args.output else ROOT / "reports" / f"rag_evaluation_{stamp}.json"
    workbook_output = Path(args.workbook_output) if args.workbook_output else (ROOT / "reports" / "rag_evaluation_kumulatif.xlsx" if args.append_workbook else excel_output_path(output))
    rows: list[dict] = []
    health: dict | None = None
    llm_fail_streak, aborted = 0, None

    try:
        health = get_json(args.api.rstrip("/") + "/kb/health")
        if health.get("status") != "ok":
            raise RuntimeError(f"API health tidak sehat: {health}")
    except Exception as exc:  # noqa: BLE001
        print(f"API belum siap; tidak ada pertanyaan dievaluasi: {exc}", file=sys.stderr)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps({
            "created_at": datetime.now(timezone.utc).isoformat(), "api": args.api,
            "planned_cases": len(golden) * len(modes), "completed_cases": 0,
            "failed_cases": 0, "not_run_cases": len(golden) * len(modes),
            "preflight_error": f"{type(exc).__name__}: {exc}",
            "results": [],
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Laporan preflight tersimpan: {output}", file=sys.stderr)
        if not args.no_excel:
            try:
                export_workbook(output, workbook_output, args.append_workbook, args.replace_existing_ids)
                print(f"Workbook hasil/preflight tersimpan: {workbook_output}", file=sys.stderr)
            except Exception as export_exc:  # noqa: BLE001
                print(f"Ekspor workbook gagal; JSON preflight tetap tersimpan: {export_exc}", file=sys.stderr)
        return 2

    for item in golden:
        for mode in modes:
            record = {
                "id": item["id"], "document_id": item.get("document_id"), "mode": mode,
                "question": item["question"], "expected_answer": item.get("expected_answer"),
                "expected_source_files": item.get("expected_source_files", []),
                "evidence_quote": item.get("evidence_quote"), "success": False,
                "run_status": "Gagal", "error": None,
            }
            try:
                result, client_ms = post_json(args.api.rstrip("/") + "/kb/query", {
                    "question": item["question"], "top_k": args.top_k,
                    "corpus": args.corpus, "mode": mode, "debug": True,
                })
                retrieval = result.get("retrieval") or {}
                candidates = retrieval.get("candidate_chunks") if "candidate_chunks" in retrieval else result.get("citations", [])
                candidates = (candidates or [])[:args.top_k]
                citations = result.get("citations") or []
                debug = result.get("debug") or {}
                context = debug.get("context_sent_to_llm")     # konteks AKTUAL (dari objek prompt final)
                generation = result.get("generation") or {}
                validation = result.get("validation") or {}
                answer = result.get("answer") or ""
                record.update({
                    "success": True,
                    "run_status": "Selesai",
                    "answer": answer,
                    "answer_mode": result.get("answer_mode"),
                    "eval_status": result.get("status"),
                    "generation": generation,
                    "final_prompt": debug.get("stage_3_4_final_prompt_sent_to_llm"),
                    "llm_raw_answer": debug.get("stage_5_llm_raw_answer"),
                    "retrieval_trace": debug.get("retrieval_trace"),
                    "retrieved_candidates": candidates,
                    "llm_context": context if context is not None else [],
                    "context_available_from_api": context is not None,
                    "context_sent_to_llm": context_to_text(context) if context is not None else None,
                    "llm_generation_attempted": retrieval.get("llm_generation_attempted"),
                    "used_citations": citations,
                    "source_ids_in_answer": citation_markers(answer),
                    "citation_ids_structurally_valid": citations_valid(answer, citations),
                    "validation": validation,
                    "retrieval": retrieval,
                    "timings_ms": result.get("timings_ms"),
                    "server_latency_ms": result.get("latency_ms"),
                    "client_latency_ms": round(client_ms, 2),
                    "evaluation_run_id": result.get("evaluation_run_id"),
                    "document_match_proxy": proxy_metrics(candidates, item.get("expected_source_files", []), args.top_k),
                })
            except Exception as exc:  # noqa: BLE001
                record["error"] = f"{type(exc).__name__}: {exc}"
                record["eval_status"] = "RETRIEVAL_ERROR" if "RETRIEVAL_ERROR" in str(exc) else "API_ERROR"
            rows.append(record)
            print(f"[{len(rows)}/{len(golden)*len(modes)}] {item['id']} {mode}: {record['run_status']} "
                  f"{record.get('eval_status')}", flush=True)
            if record.get("eval_status") in {"LLM_TIMEOUT", "LLM_RATE_LIMIT", "LLM_ERROR"}:
                llm_fail_streak += 1
            else:
                llm_fail_streak = 0
            if llm_fail_streak >= args.stop_after_llm_failures:
                aborted = (f"Run dihentikan setelah {llm_fail_streak} kegagalan LLM berturut-turut "
                           f"(status terakhir {record.get('eval_status')}); periksa kuota/limit Groq.")
                print(aborted, file=sys.stderr, flush=True)
                break
            time.sleep(max(0.0, args.delay))
        if aborted:
            break

    completed = sum(row["success"] for row in rows)
    output.parent.mkdir(parents=True, exist_ok=True)
    summary = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "golden_set": str(golden_path), "api": args.api, "top_k": args.top_k,
        "corpus": args.corpus, "modes": modes, "health_at_start": health,
        "golden_questions_total": golden_total, "golden_questions_run": len(golden), "limit": args.limit,
        "planned_cases": len(golden) * len(modes), "completed_cases": completed,
        "failed_cases": len(rows) - completed, "aborted_reason": aborted,
        "not_run_cases": len(golden) * len(modes) - len(rows),
        "status_counts": {k: sum(1 for r in rows if r.get("eval_status") == k) for k in sorted({r.get("eval_status") for r in rows if r.get("eval_status")})},
        "raw_metrics_note": "P/R/MRR/Hit berbasis filename pada JSON hanya proxy otomatis. Nilai evaluasi workbook menunggu penilaian manual relevansi chunk pada Retrieval Detail kolom J.",
        "manual_review_required": ["Chunk Mendukung Pertanyaan?", "Jumlah Klaim Faktual", "Klaim Bersitasi dan Didukung", "Faithfulness", "Correctness", "Alasan Juri", "Citation Precision"],
        "results": rows,
    }
    output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k not in {"results", "health_at_start"}}, ensure_ascii=False, indent=2))
    print(f"Hasil mentah tersimpan: {output}")

    if not args.no_excel:
        try:
            export_workbook(output, workbook_output, args.append_workbook, args.replace_existing_ids)
        except Exception as exc:  # noqa: BLE001
            print(f"Ekspor workbook gagal; JSON mentah tetap tersimpan: {exc}", file=sys.stderr)
            return 3
        print(f"Workbook hasil aktual tersimpan: {workbook_output}")
    return 0 if completed == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
