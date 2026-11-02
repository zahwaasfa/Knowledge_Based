"""Fallback writer for a completed ARCANA evaluation when Artifact Tool import stalls."""
import json
import argparse
import re
import sys
from pathlib import Path
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font
from openpyxl.workbook.properties import CalcProperties

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--template", required=True)
parser.add_argument("--results", required=True)
parser.add_argument("--output", required=True)
parser.add_argument("--legacy-log", default=str(ROOT / "reports" / "query_runs.jsonl"),
                    help="query_runs.jsonl: dipakai hanya untuk run lama yang belum punya konteks aktual/status eksplisit.")
args = parser.parse_args()
sys.path.insert(0, str(ROOT))
from kb import rag as kbrag  # noqa: E402
from kb.query_plan import GENERIC, stem as kbstem, terms as kbterms  # noqa: E402
template = Path(args.template)
results_path = Path(args.results)
output = Path(args.output)

with results_path.open(encoding="utf-8") as f:
    evaluation = json.load(f)
result_map = {(r.get("id"), r.get("mode")): r for r in evaluation.get("results", [])}
wb = load_workbook(template)
answers = wb["Evaluasi Jawaban"]
details = wb["Retrieval Detail"]
recall = wb["Recall Sumber"]
summary = wb["Ringkasan"]
guide = wb["Panduan"]

def norm_method(value):
    return "vector" if value == "Vector RAG" else "graph" if value == "Graph RAG" else None

def excel_text(value):
    """Remove XML-forbidden control bytes and respect Excel's cell text limit."""
    if value is None:
        return "", False
    text = str(value)
    cleaned = "".join(ch for ch in text if ch in "\t\n\r" or ord(ch) >= 32 and not 0xD800 <= ord(ch) <= 0xDFFF)
    truncated = len(cleaned) > 32767
    return cleaned[:32767], cleaned != text or truncated


NEW_COLS = [  # (kolom Excel, judul, lebar)
    (28, "Status Evaluasi (ANSWERED/PARTIAL/NOT_FOUND/…)", 22), (29, "Tahap Bermasalah (Retrieval/Konteks/Generasi/Sitasi/Jawaban)", 26),
    (30, "Status Retrieval", 20), (31, "Jumlah Chunk Ditemukan", 12), (32, "Jumlah Chunk di Konteks Final", 12),
    (33, "ID Chunk Terpilih (konteks final)", 40), (34, "Skor Retrieval (chunk terpilih)", 24),
    (35, "Status Request LLM", 16), (36, "Model LLM", 20), (37, "Percobaan LLM / Durasi", 22), (38, "Penyebab Error LLM (kategori, HTTP)", 30),
    (39, "Sitasi Final (chunk_id)", 40), (40, "Validitas Sitasi (detail)", 34), (41, "Dukungan Jawaban oleh Chunk (rasio leksikal 0-1)", 18),
    (42, "Klaim Tidak Didukung / Indikator Hallucination", 30), (43, "Kelengkapan vs Jawaban Referensi (proxy leksikal 0-1)", 20),
    (44, "Sumber Data Konteks", 26),
]
STATUS_TAHAP = {"ANSWERED": "-", "PARTIAL": "Jawaban (sebagian)", "NOT_FOUND": "Retrieval/Konteks", "RETRIEVAL_ERROR": "Retrieval",
                "EMPTY_CONTEXT": "Retrieval", "LLM_TIMEOUT": "Generasi", "LLM_RATE_LIMIT": "Generasi", "LLM_ERROR": "Generasi",
                "INVALID_CITATION": "Sitasi", "UNSUPPORTED_ANSWER": "Jawaban (tidak didukung)", "API_ERROR": "API"}


def load_legacy_log(path):
    out = {}
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                try:
                    rec = json.loads(line)
                    out[rec.get("run_id")] = rec
                except ValueError:
                    pass
    except OSError:
        pass
    return out


legacy_log = load_legacy_log(args.legacy_log)


def content_stems(text):
    return {kbstem(t) for t in kbterms(text or "") if t not in GENERIC and not t.isdigit()}


def derive(result):
    """Turunkan semua kolom baru dari hasil run. Run baru memakai status API; run lama divalidasi ulang dari log."""
    d = {"legacy": False}
    answer = result.get("answer") or ""
    prompt = result.get("final_prompt") or {}
    gen = result.get("generation") or {}
    cands = result.get("retrieved_candidates") or []
    cites = result.get("used_citations") or []
    context_text = prompt.get("context_text")
    sent_chunks = prompt.get("chunks")
    status = result.get("eval_status")
    validation = {}
    if status:   # run baru (setelah perbaikan)
        d["source"] = "API debug: prompt final yang benar-benar dikirim ke Groq"
        d["model"] = gen.get("model") or prompt.get("model")
        d["llm_status"] = gen.get("status")
        d["err"] = ", ".join(str(x) for x in (gen.get("error_category"), f"HTTP {gen['http_status']}" if gen.get("http_status") else None) if x)
        d["attempts"] = f"{gen.get('attempt_count', 0)} percobaan"
        d["ctx_ids"] = [c.get("chunk_id") for c in (sent_chunks or [])]
        validation = (result.get("validation") or {})
    else:        # run lama: konteks direkonstruksi dari log, status divalidasi ulang secara konservatif
        d["legacy"] = True
        lg = legacy_log.get(result.get("evaluation_run_id")) or {}
        ctx = lg.get("llm_context") or []
        by_chunk = {c.get("chunk_id"): c for c in ctx}
        d["source"] = "LEGACY: direkonstruksi dari query_runs.jsonl (API lama tidak mengekspos konteks aktual)" if ctx else "LEGACY: tidak tersedia"
        d["ctx_ids"] = [c.get("chunk_id") for c in ctx]
        d["model"] = (result.get("health_model") or "model Groq pada .env (tidak diubah)")
        context_text = "\n\n".join(f"[{i}] chunk: {c.get('chunk_id')}; dokumen: {c.get('title')}\nISI SUMBER: {c.get('text')}" for i, c in enumerate(ctx, 1)) or None
        gms = (result.get("timings_ms") or {}).get("generation")
        if result.get("answer_mode") == "llm":
            d["llm_status"] = "generated"; d["err"] = ""
            sent = []
            for k, c in enumerate(cites, 1):
                row = by_chunk.get(c.get("chunk_id"))
                if row:
                    sent.append({"n": k, "chunk_id": c["chunk_id"], "text": row.get("text", ""), "neighbors": []})
            v = kbrag.validate_answer(answer, sent) if sent else None
            if v:
                validation = v
                status = kbrag.eval_status_for(answer, v)
            else:
                status = "INVALID_CITATION"
        else:
            status = "LLM_ERROR"
            d["llm_status"] = "failed"
            d["err"] = f"penyebab tidak tercatat (run lama); gagal dalam {gms} ms"
        d["attempts"] = f"tidak tercatat; generasi {gms} ms"
    d["status"] = status or "API_ERROR"
    n_cand = len(cands)
    d["n_cand"] = (result.get("retrieval") or {}).get("candidate_count", n_cand)
    d["n_ctx"] = len(d.get("ctx_ids") or [])
    hit = (result.get("document_match_proxy") or {}).get("hit_rate_at_k_expected_file_proxy")
    d["retrieval_status"] = "KOSONG" if not n_cand else ("OK (dokumen expected ada di top-k)" if hit else "TIDAK_RELEVAN (dokumen expected tidak di top-k, proxy)")
    d["scores"] = ", ".join(f"{c.get('chunk_id')}={round(c['score'],3)}" for c in cands if isinstance(c.get("score"), (int, float)))
    d["cite_ids"] = ", ".join(c.get("chunk_id") or "" for c in cites)
    inv = validation.get("invalid_markers") or []
    d["cite_detail"] = (f"struktur={'valid' if result.get('citation_ids_structurally_valid') else 'tidak valid/tanpa sitasi'}; "
                        f"nomor tak dikenal={inv or 'tidak ada'}; klaim tanpa sitasi={validation.get('uncited_claims', 'n/a')}")
    d["support"] = validation.get("support_ratio")
    uns = validation.get("unsupported_claims")
    d["halluc"] = ("tidak terdeteksi (heuristik leksikal)" if uns == 0 else f"{uns} klaim tidak didukung: " + " | ".join(validation.get("unsupported_segments", []))[:300]) if uns is not None else "belum dinilai"
    exp = content_stems(result.get("expected_answer"))
    d["complete"] = round(len(exp & content_stems(answer)) / len(exp), 3) if exp and d["llm_status"] == "generated" else None
    tahap = STATUS_TAHAP.get(d["status"], "-")
    if d["status"] == "NOT_FOUND" and hit:
        tahap = "Konteks/Generasi (dokumen expected ada di kandidat, tetapi dijawab tidak ditemukan)"
    elif d["status"] == "ANSWERED" and cands and not hit:
        tahap = "Retrieval (jawaban ada, tetapi dokumen expected tidak di top-k)"
    d["tahap"] = tahap
    d["context_text"] = context_text
    return d

answer_rows = {}
for r in range(5, 155):
    answer_rows[(answers.cell(r, 1).value, answers.cell(r, 7).value)] = r

detail_rows = {}
for r in range(5, 755):
    key = (details.cell(r, 1).value, details.cell(r, 2).value, details.cell(r, 3).value)
    detail_rows[key] = r

for (golden_id, method), row in answer_rows.items():
    result = result_map.get((golden_id, norm_method(method)))
    if not result:
        answers.cell(row, 26, "Belum dijalankan")
        continue
    answers.cell(row, 26, "Selesai" if result.get("success") else "Gagal")
    answers.cell(row, 27, result.get("evaluation_run_id") or "")
    if not result.get("success"):
        answers.cell(row, 25, f"Run gagal; hasil lama dipertahankan. {result.get('error', '')}".strip())
        answers.cell(row, 24, result.get("eval_status") or "API_ERROR")
        answers.cell(row, 28, result.get("eval_status") or "API_ERROR")
        continue
    d = derive(result)
    context = d["context_text"]
    if context is None:
        context = ("Tidak ada konteks yang dikirim ke LLM pada run ini (status: %s)." % d["status"]
                   if d["status"] in ("EMPTY_CONTEXT", "RETRIEVAL_ERROR") else "Konteks aktual tidak tersedia pada run ini.")
    context, context_cleaned = excel_text(context)
    answer, answer_cleaned = excel_text(result.get("answer") or "")
    answers.cell(row, 8, context)
    answers.cell(row, 9, answer)
    answers.cell(row, 10, ", ".join(result.get("source_ids_in_answer") or []))
    answers.cell(row, 11, None)  # claim count needs human review
    answers.cell(row, 12, None)  # supported claim count needs human review
    valid = result.get("citation_ids_structurally_valid")
    answers.cell(row, 13, "Ya" if valid is True else "Tidak" if valid is False else "Belum dinilai")
    for col in (18, 19, 20, 21):  # judge scores/reason and citation precision
        answers.cell(row, col, None)
    latency = result.get("client_latency_ms", result.get("server_latency_ms"))
    answers.cell(row, 23, round(latency / 1000, 3) if isinstance(latency, (float, int)) else None)
    answers.cell(row, 24, d["status"])        # Kelas Kegagalan = status eksplisit (ANSWERED = tidak gagal)
    vals = {29: d["tahap"], 30: d["retrieval_status"], 31: d["n_cand"], 32: d["n_ctx"], 33: ", ".join(d.get("ctx_ids") or []),
            34: d["scores"], 35: d["llm_status"], 36: d["model"], 37: d["attempts"], 38: d["err"], 39: d["cite_ids"],
            40: d["cite_detail"], 41: d["support"], 42: d["halluc"], 43: d["complete"], 44: d["source"]}
    answers.cell(row, 28, d["status"])
    for col, v in vals.items():
        answers.cell(row, col, excel_text(v)[0] if isinstance(v, str) else v)
    notes = ["Penilaian manual masih diperlukan: jumlah klaim, faithfulness, correctness, citation precision (kolom K, L, R-U)."]
    if d["legacy"]:
        notes.append("Run LEGACY (sebelum perbaikan): status diturunkan ulang dari data yang ada; tidak dijalankan ulang.")
    if d["status"] in ("LLM_ERROR", "LLM_TIMEOUT", "LLM_RATE_LIMIT"):
        notes.append("Kegagalan teknis generasi LLM — BUKAN 'informasi tidak ditemukan'. Retrieval berhasil; jawaban tidak dibuat.")
    if answer_cleaned:
        notes.append("Jawaban API mengandung karakter kontrol atau melebihi batas sel Excel; teks pada matriks dibersihkan/dipotong. JSON mentah menyimpan payload asli.")
    if context_cleaned:
        notes.append("Konteks pada matriks dibersihkan/dipotong untuk batas karakter Excel; JSON mentah menyimpan payload asli.")
    answers.cell(row, 25, " ".join(notes))

    candidates = (result.get("retrieved_candidates") or [])[:5]
    for rank in range(1, 6):
        detail_row = detail_rows.get((golden_id, method, rank))
        if not detail_row:
            continue
        if rank > len(candidates):
            for col in (4, 5, 6, 7, 10, 11):
                details.cell(detail_row, col, None)
            details.cell(detail_row, 12, None)
            continue
        candidate = candidates[rank - 1]
        details.cell(detail_row, 4, candidate.get("chunk_id") or "")
        details.cell(detail_row, 5, candidate.get("doc_id") or "")
        details.cell(detail_row, 6, candidate.get("file_name") or "")
        score = candidate.get("score")
        details.cell(detail_row, 7, score if isinstance(score, (int, float)) else None)
        details.cell(detail_row, 10, "Belum dinilai")
        note, _ = excel_text(candidate.get("snippet") or "")
        retrieval_methods = candidate.get("retrieval_methods") or []
        if retrieval_methods:
            note += ("\n" if note else "") + "Metode retrieval: " + ", ".join(retrieval_methods)
        details.cell(detail_row, 11, note)
        details.cell(detail_row, 12, "Ya")

# Filename match is formula-driven; semantic relevance stays a manual judgement.
for r in range(5, 755):
    details.cell(r, 8, f'=IF(OR(F{r}="",L{r}<>"Ya"),"",IF(ISNUMBER(SEARCH(F{r},I{r})),"Ya","Tidak"))')

# Precision/recall/ranking only resolve after each recorded candidate is manually reviewed.
for r in range(5, 155):
    run = "'Evaluasi Jawaban'!$Z$5:$Z$154"
    did = "'Retrieval Detail'!$A$5:$A$754"
    meth = "'Retrieval Detail'!$B$5:$B$754"
    recorded = "'Retrieval Detail'!$L$5:$L$754"
    match = "'Retrieval Detail'!$H$5:$H$754"
    support = "'Retrieval Detail'!$J$5:$J$754"
    done = f'COUNTIFS(\'Evaluasi Jawaban\'!$A$5:$A$154,A{r},\'Evaluasi Jawaban\'!$G$5:$G$154,G{r},{run},"Selesai")>0'
    unresolved = f'COUNTIFS({did},A{r},{meth},G{r},{recorded},"Ya",{support},"<>Ya",{support},"<>Tidak")>0'
    denominator = f'COUNTIFS({did},A{r},{meth},G{r},{recorded},"Ya")'
    numerator = f'COUNTIFS({did},A{r},{meth},G{r},{recorded},"Ya",{match},"Ya",{support},"Ya")'
    answers.cell(r, 14, f'=IF(NOT({done}),"",IF({unresolved},"",IF({denominator}=0,"",{numerator}/{denominator})))')
    recall_n = f'COUNTIFS(\'Recall Sumber\'!$A$5:$A$154,A{r},\'Recall Sumber\'!$B$5:$B$154,G{r})'
    recall_y = f'COUNTIFS(\'Recall Sumber\'!$A$5:$A$154,A{r},\'Recall Sumber\'!$B$5:$B$154,G{r},\'Recall Sumber\'!$D$5:$D$154,"Ya")'
    answers.cell(r, 15, f'=IF(NOT({done}),"",IF({unresolved},"",IF({recall_n}=0,"",{recall_y}/{recall_n})))')
    rr = "".join(f'IF(COUNTIFS({did},A{r},{meth},G{r},\'Retrieval Detail\'!$C$5:$C$754,{rank},{match},"Ya",{support},"Ya",{recorded},"Ya")>0,{1/rank:.6f},' for rank in range(1, 6))
    answers.cell(r, 16, f'=IF(NOT({done}),"",IF({unresolved},"",{rr}0{(")" * 5)}))')
    hit = f'COUNTIFS({did},A{r},{meth},G{r},{match},"Ya",{support},"Ya",{recorded},"Ya")'
    answers.cell(r, 17, f'=IF(NOT({done}),"",IF({unresolved},"",IF({hit}>0,1,0)))')
    answers.cell(r, 22, f'=IF(OR(Z{r}<>"Selesai",K{r}="",K{r}=0,L{r}="",L{r}>K{r}),"",L{r}/K{r})')

for r in range(5, 155):
    recall.cell(r, 4, f'=IF(COUNTIFS(\'Evaluasi Jawaban\'!$A$5:$A$154,A{r},\'Evaluasi Jawaban\'!$G$5:$G$154,B{r},\'Evaluasi Jawaban\'!$Z$5:$Z$154,"Selesai")=0,"",IF(COUNTIFS(\'Retrieval Detail\'!$A$5:$A$754,A{r},\'Retrieval Detail\'!$B$5:$B$754,B{r},\'Retrieval Detail\'!$L$5:$L$754,"Ya",\'Retrieval Detail\'!$H$5:$H$754,"Ya",\'Retrieval Detail\'!$J$5:$J$754,"<>Ya",\'Retrieval Detail\'!$J$5:$J$754,"<>Tidak")>0,"",IF(COUNTIFS(\'Retrieval Detail\'!$A$5:$A$754,A{r},\'Retrieval Detail\'!$B$5:$B$754,B{r},\'Retrieval Detail\'!$F$5:$F$754,C{r},\'Retrieval Detail\'!$C$5:$C$754,"<=5",\'Retrieval Detail\'!$H$5:$H$754,"Ya",\'Retrieval Detail\'!$J$5:$J$754,"Ya",\'Retrieval Detail\'!$L$5:$L$754,"Ya")>0,"Ya","Tidak")))')

# Summary formulas exclude failed/not-run pairs and leave unrated semantic metrics blank.
for r in range(6, 16):
    src_col = {6:"N",7:"O",8:"P",9:"Q",10:"R",11:"S",13:"U",14:"V",15:"W"}.get(r)
    if r == 12:
        for col, method in ((2,"Vector RAG"),(3,"Graph RAG")):
            summary.cell(r,col, f'=IFERROR(COUNTIFS(\'Evaluasi Jawaban\'!$G$5:$G$154,"{method}",\'Evaluasi Jawaban\'!$M$5:$M$154,"Ya")/(COUNTIFS(\'Evaluasi Jawaban\'!$G$5:$G$154,"{method}",\'Evaluasi Jawaban\'!$M$5:$M$154,"Ya")+COUNTIFS(\'Evaluasi Jawaban\'!$G$5:$G$154,"{method}",\'Evaluasi Jawaban\'!$M$5:$M$154,"Tidak")),"")')
    elif src_col:
        for col, method in ((2,"Vector RAG"),(3,"Graph RAG")):
            summary.cell(r,col, f'=IF(COUNTIFS(\'Evaluasi Jawaban\'!$G$5:$G$154,"{method}",\'Evaluasi Jawaban\'!$Z$5:$Z$154,"Selesai")=0,"",IFERROR(AVERAGEIFS(\'Evaluasi Jawaban\'!${src_col}$5:${src_col}$154,\'Evaluasi Jawaban\'!$G$5:$G$154,"{method}",\'Evaluasi Jawaban\'!$Z$5:$Z$154,"Selesai"),""))')
summary.cell(16,1,"Run selesai")
for col, method in ((2,"Vector RAG"),(3,"Graph RAG")):
    summary.cell(16,col, f'=COUNTIFS(\'Evaluasi Jawaban\'!$G$5:$G$154,"{method}",\'Evaluasi Jawaban\'!$Z$5:$Z$154,"Selesai")')
summary["A17"] = '=\"Run gagal — Vector RAG: \"&COUNTIFS(\'Evaluasi Jawaban\'!$G$5:$G$154,\"Vector RAG\",\'Evaluasi Jawaban\'!$Z$5:$Z$154,\"Gagal\")&\"; Graph RAG: \"&COUNTIFS(\'Evaluasi Jawaban\'!$G$5:$G$154,\"Graph RAG\",\'Evaluasi Jawaban\'!$Z$5:$Z$154,\"Gagal\")'

guide["B14"] = "Kandidat Top-5 dari file expected yang juga dinilai relevan (Retrieval Detail J=Ya) dibagi kandidat aktual; kosong sampai semua kandidat dinilai."
guide["C14"] = "Chunk dari dokumen expected belum otomatis relevan; reviewer perlu memeriksa isi kandidat."
guide["B15"] = "File expected unik yang ditemukan melalui chunk relevan dibagi seluruh file expected unik; kosong sampai dinilai."
guide["B16"] = "Reciprocal rank kemunculan pertama chunk expected yang dinilai relevan; 0 jika selesai tanpa hasil relevan."
guide["C16"] = "Rank dari urutan retrieval API."
guide["B17"] = "1 jika ada chunk expected yang dinilai relevan, 0 jika tidak ada; kosong sebelum penilaian."
guide["B18"] = "Metrik relevansi menunggu penilaian manual pada kolom J. Status run mencegah data belum dijalankan dihitung sebagai nol."
guide["A24"] = "Status run tercatat di Evaluasi Jawaban kolom Z; ID API ada di kolom AA."
summary["E6"] = "Top-5 chunk expected yang dinilai relevan ÷ kandidat aktual; menunggu tinjauan manual."
summary["E7"] = "File expected unik ditemukan melalui chunk relevan ÷ seluruh file expected unik."
summary["E8"] = "Reciprocal rank chunk expected relevan pertama; 0 bila run selesai tanpa hasil relevan."
summary["E9"] = "Proporsi run selesai dengan setidaknya satu chunk expected relevan."
answers["Z4"] = "Status Run (Selesai/Gagal/Belum dijalankan)"
answers["AA4"] = "Evaluation Run ID API"
answers.column_dimensions["Z"].width = 30
answers.column_dimensions["AA"].width = 38
for row in answers.iter_rows(min_row=4, max_row=154, min_col=26, max_col=27):
    for cell in row:
        cell.alignment = Alignment(wrap_text=True)

# ---- Kolom baru (ditambahkan di kanan; kolom lama tidak dihapus/digeser) ----
from copy import copy
hdr_src = answers.cell(4, 27)
for col, title, width in NEW_COLS:
    c = answers.cell(4, col, title)
    c.font, c.fill, c.border, c.alignment = copy(hdr_src.font), copy(hdr_src.fill), copy(hdr_src.border), copy(hdr_src.alignment)
    answers.column_dimensions[c.column_letter].width = width
for row in answers.iter_rows(min_row=5, max_row=154, min_col=28, max_col=44):
    for cell in row:
        cell.alignment = Alignment(wrap_text=True, vertical="top")

# ---- Ringkasan: hitung per status eksplisit ----
STATUSES = ["ANSWERED", "PARTIAL", "NOT_FOUND", "RETRIEVAL_ERROR", "EMPTY_CONTEXT", "LLM_TIMEOUT", "LLM_RATE_LIMIT", "LLM_ERROR", "INVALID_CITATION", "UNSUPPORTED_ANSWER"]
summary.cell(19, 1, "Distribusi status evaluasi (kolom AB Evaluasi Jawaban)")
summary.cell(19, 1).font = copy(summary.cell(4, 1).font)
for i, st in enumerate(STATUSES):
    r = 20 + i
    summary.cell(r, 1, st)
    for col, method in ((2, "Vector RAG"), (3, "Graph RAG")):
        summary.cell(r, col, f'=COUNTIFS(\'Evaluasi Jawaban\'!$G$5:$G$154,"{method}",\'Evaluasi Jawaban\'!$AB$5:$AB$154,"{st}")')
    summary.cell(r, 4, f"=C{r}-B{r}")
summary.cell(20 + len(STATUSES), 1, "Catatan: LLM_TIMEOUT/LLM_RATE_LIMIT/LLM_ERROR = kegagalan teknis generasi, bukan 'informasi tidak ditemukan'. Support/hallucination = heuristik leksikal, bukan kebenaran objektif.")

# ---- Sheet dokumentasi: legenda status, akar masalah, baseline sebelum perbaikan ----
if "Status & Perubahan" in wb.sheetnames:
    del wb["Status & Perubahan"]
doc = wb.create_sheet("Status & Perubahan")
baseline = ROOT / "reports" / "rag_evaluation_20_10_2026.json"
rows_doc = [
    ("Legenda status evaluasi (kolom AB / X pada Evaluasi Jawaban)", ""),
    ("ANSWERED", "Jawaban dibuat LLM, semua sitasi valid terhadap chunk yang dikirim, dukungan leksikal memadai."),
    ("PARTIAL", "Sebagian pertanyaan terjawab; jawaban menyatakan bagian yang belum ditemukan."),
    ("NOT_FOUND", "Retrieval & LLM berhasil, tetapi LLM menyatakan bukti tidak cukup (tanpa sitasi)."),
    ("RETRIEVAL_ERROR", "Pencarian chunk gagal (exception/HTTP 503 dari API)."),
    ("EMPTY_CONTEXT", "Tidak ada chunk yang dapat dikirim; LLM tidak dipanggil."),
    ("LLM_TIMEOUT / LLM_RATE_LIMIT / LLM_ERROR", "Kegagalan teknis generasi (setelah retry terbatas). Bukan 'informasi tidak ditemukan'."),
    ("INVALID_CITATION", "Nomor sitasi tidak dikenal atau tidak ada sitasi sama sekali pada klaim faktual."),
    ("UNSUPPORTED_ANSWER", "Mayoritas kalimat bersitasi tidak didukung chunk yang dikutip (heuristik leksikal: istilah isi & angka)."),
    ("", ""),
    ("Catatan metode", "Dukungan/hallucination memakai heuristik leksikal deterministik (bukan LLM-judge dan bukan kebenaran objektif); Faithfulness/Correctness (kolom R-S) tetap penilaian manual/juri."),
    ("", ""),
    ("Akar masalah yang diperbaiki", ""),
    ("1", "Query memanggil Groq DUA kali (retrieval.answer lalu kb_api.query) sehingga kuota/limit cepat habis."),
    ("2", "Semua exception LLM dipetakan ke satu pesan 'timeout atau pembatasan antrean'; kegagalan instan (~100 ms) tidak dapat dibedakan dari timeout."),
    ("3", "debug.context_sent_to_llm tidak pernah diisi API; konteks log termutasi (nomor n ganda) oleh renumbering sitasi."),
    ("4", "Graph RAG mencampur hasil vector; sitasi dapat ditambahkan paksa ' [1]' tanpa dukungan; nomor sitasi tidak divalidasi terhadap konteks terkirim."),
    ("5", "Chunk transkrip hanya satu giliran bicara (~180-370 karakter) sehingga konteks terlalu tipis; kini Graph RAG menambah saudara SUB_CHUNK_OF."),
]
if baseline.is_file():
    try:
        b = json.load(open(baseline, encoding="utf-8"))["results"]
        ok = [r for r in b if r.get("answer_mode") == "llm"]
        bad = [r for r in b if r.get("answer_mode") != "llm"]
        gms = sorted((r.get("timings_ms") or {}).get("generation", 0) for r in bad)
        rows_doc += [("", ""), ("Baseline SEBELUM perbaikan (run 20/10/2026, 150 kasus)", ""),
                     ("Jawaban LLM berhasil", f"{len(ok)} (Graph {sum(r['mode']=='graph' for r in ok)}, Vector {sum(r['mode']=='vector' for r in ok)})"),
                     ("Pesan 'timeout/antrean'", f"{len(bad)} (Graph {sum(r['mode']=='graph' for r in bad)}, Vector {sum(r['mode']=='vector' for r in bad)})"),
                     ("Durasi generasi pada kegagalan", f"median {gms[len(gms)//2]:.0f} ms, min {gms[0]:.0f} ms — gagal terlalu cepat untuk timeout jaringan"),
                     ("Graph RAG yang memuat hasil vector", f"{sum(1 for r in b if r['mode']=='graph' and (r.get('retrieval') or {}).get('vector_results'))} dari 75"),
                     ("Hasil SESUDAH perbaikan", "BELUM DIJALANKAN: API ARCANA/Neo4j/Groq tidak dapat diakses dari lingkungan perbaikan. Jalankan scripts/evaluate_rag.py (lihat README_PERBAIKAN.md).")]
    except Exception:  # noqa: BLE001
        pass
for i, (a_, b_) in enumerate(rows_doc, 1):
    doc.cell(i, 1, a_)
    doc.cell(i, 2, b_)
    if b_ == "" and a_:
        doc.cell(i, 1).font = Font(bold=True)
doc.column_dimensions["A"].width = 44
doc.column_dimensions["B"].width = 130
for row in doc.iter_rows(min_row=1, max_row=len(rows_doc), max_col=2):
    for cell in row:
        cell.alignment = Alignment(wrap_text=True, vertical="top")

wb.calculation = CalcProperties(calcMode="auto", fullCalcOnLoad=True, forceFullCalc=True)
wb.save(output)
check = load_workbook(output, data_only=False)
check_answers = check["Evaluasi Jawaban"]
check_details = check["Retrieval Detail"]
statuses = [check_answers.cell(r, 26).value for r in range(5, 155)]
failure_classes = [check_answers.cell(r, 24).value for r in range(5, 155)]
recorded = sum(check_details.cell(r, 12).value == "Ya" for r in range(5, 755))
manual_pending = sum(check_details.cell(r, 10).value == "Belum dinilai" for r in range(5, 755) if check_details.cell(r, 12).value == "Ya")
formula_ranges = [("Evaluasi Jawaban", "N5:Q154"), ("Evaluasi Jawaban", "V5:V154"),
                  ("Retrieval Detail", "H5:H754"), ("Recall Sumber", "D5:D154"),
                  ("Ringkasan", "B6:C17")]
formula_count = sum(1 for sheet_name, area in formula_ranges for row in check[sheet_name][area]
                    for cell in (row if isinstance(row, tuple) else (row,))
                    if isinstance(cell.value, str) and cell.value.startswith("="))
print(json.dumps({"output": str(output), "questions": evaluation.get("golden_questions_run"),
                  "completed": evaluation.get("completed_cases"), "failed": evaluation.get("failed_cases"),
                  "sheets": check.sheetnames, "status_counts": {s: statuses.count(s) for s in set(statuses)},
                  "retrieval_candidates_recorded": recorded, "candidate_manual_reviews_pending": manual_pending,
                  "status_evaluasi": {s: failure_classes.count(s) for s in set(failure_classes)},
                  "formula_cells": formula_count,
                  "review_fields": ["chunk relevance", "claim counts", "faithfulness", "correctness", "citation precision"]}, ensure_ascii=False))
