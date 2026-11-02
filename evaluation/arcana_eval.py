"""ARCANA - analisis offline Graph RAG vs Vector RAG dari workbook hasil pengujian.

Modul ini TIDAK memanggil Neo4j, Groq, atau API ARCANA. Ia hanya membaca workbook Excel,
memvalidasi, menghitung ulang metrik yang dapat diverifikasi, dan menulis workbook baru.
Satuan analisis: pasangan (Question ID, Metode). Pembanding berpasangan: Question ID yang sama.
"""
from __future__ import annotations
import json, re, math
from pathlib import Path
import numpy as np
import pandas as pd

K_DEFAULT = 5
CORRECT_MIN = 4      # Answer Correctness >= 4 -> "Terjawab benar"
PARTIAL_VALUE = 3    # == 3 -> "Terjawab sebagian"; <= 2 -> "Tidak terjawab / salah"
GRAPH, VECTOR = "Graph RAG", "Vector RAG"
ABSTAIN_STATUS = {"NOT_FOUND", "UNSUPPORTED_ANSWER"}
SYSTEM_FAIL_STATUS = {"RETRIEVAL_ERROR", "LLM_ERROR", "LLM_TIMEOUT", "LLM_RATE_LIMIT", "API_ERROR", "TIMEOUT", "ERROR"}
LABELS = ["Terjawab benar", "Terjawab sebagian", "Tidak terjawab / salah"]
STATUS_TO_PRED = {"ANSWERED": LABELS[0], "PARTIAL": LABELS[1], "NOT_FOUND": LABELS[2], "UNSUPPORTED_ANSWER": LABELS[2]}

# nama sheet -> daftar alias yang diterima (huruf besar/kecil diabaikan)
SHEET_ALIASES = {
    "results":   ["Raw Results", "Permintaan"],
    "retrieval": ["Raw Retrieval", "Retrieval Detail"],
    "context":   ["Raw LLM Context", "Konteks LLM"],
    "review":    ["Manual Review", "Review Manual"],
    "golden":    ["Golden Set"],
    "history":   ["Run History", "Riwayat Run"],
    "config":    ["Run Config", "Konfigurasi"],
    "trace":     ["Raw Trace", "Trace"],
}
REQUIRED_SHEETS = ["results", "retrieval"]          # tanpa ini analisis tidak bisa jalan
# kolom kanonik -> alias nama kolom
COLUMN_ALIASES = {
    "results": {
        "session": ["Session ID"], "qid": ["Question ID"], "doc": ["Document ID"], "method": ["Metode", "Method"],
        "question": ["Pertanyaan"], "ref_answer": ["Jawaban acuan"], "expected_files": ["Expected source files"],
        "api_ok": ["API berhasil"], "status": ["Status evaluasi"], "answer": ["Jawaban"], "citations": ["Sitasi (JSON)"],
        "latency": ["Latency klien (ms)"], "latency_server": ["Latency server (ms)"], "gen_status": ["Status generation"],
        "error": ["Error generation/request"], "faith": ["Faithfulness"], "corr": ["Answer Correctness"],
        "relev": ["Answer Relevancy"], "label_actual": ["Label aktual"],
    },
    "retrieval": {
        "session": ["Session ID"], "qid": ["Question ID"], "method": ["Metode", "Method"], "rank": ["Rank"],
        "chunk_id": ["Chunk ID"], "doc": ["Document ID"], "file": ["File sumber"], "expected_flag": ["Sumber diharapkan"],
        "snippet": ["Snippet / isi chunk"],
    },
    "context": {
        "qid": ["Question ID"], "method": ["Metode", "Method"], "order": ["Urutan konteks"], "chunk_id": ["Chunk ID"],
        "doc": ["Document ID"], "text": ["Teks konteks aktual dikirim ke LLM"],
    },
    "review": {
        "qid": ["Question ID"], "method": ["Metode", "Method"], "item": ["Metrik / item review"],
        "value": ["Nilai manual"], "status": ["Status"], "note": ["Catatan verifikasi"],
    },
    "golden": {
        "qid": ["Question ID", "id"], "doc": ["Document ID", "document_id"], "question": ["Pertanyaan", "question"],
        "ref_answer": ["Jawaban acuan", "expected_answer"], "expected_files": ["Expected source files", "expected_source_files"],
        "evidence": ["Evidence quote", "evidence_quote"],
    },
}
REQUIRED_COLS = {
    "results": ["qid", "doc", "method", "status"],
    "retrieval": ["qid", "method", "rank", "doc"],
}
OPTIONAL_NOTE = {"results": ["question", "ref_answer", "expected_files", "latency", "faith", "corr", "relev", "citations"],
                 "retrieval": ["file", "expected_flag"]}


class DataFormatError(Exception):
    """Pesan kesalahan yang dimaksudkan untuk dibaca pengguna."""


# --------------------------------------------------------------------------- memuat
def _norm(s): return re.sub(r"\s+", " ", str(s)).strip().casefold()


def load_input(path, sheet_map=None, column_map=None):
    """Baca workbook. sheet_map={'results':'NamaSheet'}; column_map={'results':{'qid':'NamaKolom'}}.
    Mengembalikan (data: dict[str, DataFrame berkolom kanonik], report: DataFrame)."""
    sheet_map, column_map = sheet_map or {}, column_map or {}
    try:
        xl = pd.ExcelFile(path)
    except Exception as e:
        raise DataFormatError(f"File tidak dapat dibaca sebagai Excel (.xlsx): {e}")
    names = {_norm(n): n for n in xl.sheet_names}
    data, rows = {}, []
    raw = {}
    for key, aliases in SHEET_ALIASES.items():
        chosen = sheet_map.get(key)
        if chosen is None:
            chosen = next((names[_norm(a)] for a in aliases if _norm(a) in names), None)
        if chosen is None or chosen not in xl.sheet_names:
            if key in REQUIRED_SHEETS:
                raise DataFormatError(
                    f"Sheet wajib '{key}' tidak ditemukan. Nama yang diterima: {aliases}. "
                    f"Sheet di file: {xl.sheet_names}. Gunakan SHEET_MAP={{'{key}': 'nama sheet Anda'}}.")
            rows.append(dict(sheet_logis=key, sheet_file=None, baris=0, status="tidak ada (opsional)", kolom_tidak_terpetakan=""))
            continue
        df = xl.parse(chosen).dropna(how="all")
        df = df.loc[:, [c for c in df.columns if not str(c).startswith("Unnamed")]]
        raw[key] = df.reset_index(drop=True)
        cmap, missing = {}, []
        if key in COLUMN_ALIASES:
            cols_norm = {_norm(c): c for c in df.columns}
            for canon, aliases_c in COLUMN_ALIASES[key].items():
                src = (column_map.get(key) or {}).get(canon)
                if src is None:
                    src = next((cols_norm[_norm(a)] for a in aliases_c if _norm(a) in cols_norm), None)
                if src is not None and src in df.columns: cmap[canon] = src
                elif canon in REQUIRED_COLS.get(key, []): missing.append(canon)
            if missing:
                raise DataFormatError(
                    f"Sheet '{chosen}' kehilangan kolom wajib {missing}. Kolom tersedia: {list(df.columns)}. "
                    f"Gunakan COLUMN_MAP={{'{key}': {{'{missing[0]}': 'nama kolom Anda'}}}}.")
            out = pd.DataFrame({canon: df[src] for canon, src in cmap.items()})
            for canon in COLUMN_ALIASES[key]:
                if canon not in out: out[canon] = np.nan
            data[key] = out.reset_index(drop=True)
            unmapped = [c for c in df.columns if c not in cmap.values()]
        else:
            data[key] = df.reset_index(drop=True); unmapped = []
        rows.append(dict(sheet_logis=key, sheet_file=chosen, baris=len(df), status="OK", kolom_tidak_terpetakan=", ".join(map(str, unmapped))[:120]))
    data["raw"] = raw
    report = pd.DataFrame(rows)
    for c in ["qid", "doc", "method"]:
        for k in ("results", "retrieval"):
            data[k][c] = data[k][c].astype(str).str.strip()
    for k in ("context", "review"):
        if k in data:
            for c in ("qid", "method"): data[k][c] = data[k][c].astype(str).str.strip()
    meths = set(data["results"]["method"])
    unknown = meths - {GRAPH, VECTOR}
    if unknown:
        raise DataFormatError(f"Nilai kolom Metode tidak dikenali: {sorted(unknown)}. Diharapkan 'Graph RAG' dan 'Vector RAG'.")
    return data, report


def _to_bool(v):
    if isinstance(v, (bool, np.bool_)): return bool(v)
    if v is None or (isinstance(v, float) and math.isnan(v)): return None
    if isinstance(v, (int, float, np.integer, np.floating)): return bool(v)
    s = str(v).strip().casefold()
    if s in {"true", "1", "ya", "yes", "=true()"}: return True
    if s in {"false", "0", "tidak", "no", "=false()"}: return False
    return None


def parse_files(v):
    if v is None or (isinstance(v, float) and math.isnan(v)): return []
    if isinstance(v, (list, tuple)): return [str(x) for x in v]
    s = str(v).strip()
    if s.startswith("["):
        try: return [str(x) for x in json.loads(s)]
        except Exception: pass
    return [p.strip() for p in re.split(r"[;|\n]", s) if p.strip()]


def stem(name): return re.sub(r"\.(md|txt|pdf|docx|json)$", "", str(name).replace("\\", "/").rsplit("/", 1)[-1].strip().casefold())


def cited_docs(js):
    try: items = json.loads(js) if isinstance(js, str) else []
    except Exception: return None
    return [str(i.get("doc_id")) for i in items if isinstance(i, dict)]


def load_golden_json(path):
    g = json.load(open(path, encoding="utf-8"))
    return pd.DataFrame([{"qid": x["id"], "doc": x["document_id"], "question": x["question"], "ref_answer": x["expected_answer"],
                          "expected_files": json.dumps(x["expected_source_files"], ensure_ascii=False),
                          "evidence": x.get("evidence_quote")} for x in g])


# --------------------------------------------------------------------------- validasi
def validate(data, k=K_DEFAULT):
    """Kembalikan (issues, case_table). case_table = satu baris per (qid, metode) dengan status kelayakan + alasan eksklusi.
    Tidak ada baris yang dihapus."""
    R, T = data["results"].copy(), data["retrieval"].copy()
    issues = []
    def add(check, sev, n, detail=""): issues.append(dict(pemeriksaan=check, tingkat=sev, jumlah=int(n), keterangan=detail))
    dup = R.duplicated(["qid", "method"], keep=False)
    add("Duplikasi (Question ID, Metode) di Raw Results", "ERROR" if dup.any() else "OK", dup.sum(),
        "Duplikat dipertahankan di tabel kasus; hanya baris TERAKHIR dipakai untuk analisis." if dup.any() else "")
    piv = R.groupby("qid")["method"].nunique()
    orphan = piv[piv < 2].index.tolist()
    add("Pertanyaan tanpa pasangan metode lain", "ERROR" if orphan else "OK", len(orphan), ", ".join(orphan[:10]))
    rr = R.groupby("qid")["ref_answer"].nunique(dropna=True); rq = R.groupby("qid")["question"].nunique(dropna=True)
    add("Pertanyaan/jawaban acuan berbeda antara Graph dan Vector (ID sama)", "ERROR" if ((rr > 1) | (rq > 1)).any() else "OK",
        ((rr > 1) | (rq > 1)).sum())
    dd = R.groupby("qid")["doc"].nunique(); add("Dokumen target tidak konsisten antar metode", "ERROR" if (dd > 1).any() else "OK", (dd > 1).sum())
    for c in ["question", "ref_answer", "expected_files", "answer", "status", "api_ok", "latency", "faith", "corr", "relev"]:
        n = R[c].isna().sum() if c in R else len(R)
        add(f"Nilai kosong: {c}", "OK" if n == 0 else "PERINGATAN", n, "" if c in R and R[c].notna().any() else "kolom tidak tersedia")
    for c in ["latency", "faith", "corr", "relev"]:
        bad = pd.to_numeric(R[c], errors="coerce").isna() & R[c].notna()
        add(f"Tipe data non-numerik: {c}", "OK" if not bad.any() else "ERROR", bad.sum())
    st = R["status"].fillna("(kosong)")
    for s in sorted(set(st)): add(f"Status evaluasi = {s}", "INFO", (st == s).sum())
    api_fail = R["api_ok"].map(_to_bool).eq(False)
    add("API tidak berhasil (kegagalan sistem)", "OK" if not api_fail.any() else "ERROR", api_fail.sum())
    gen_fail = ~R["gen_status"].fillna("generated").astype(str).str.casefold().isin(["generated", "ok", "success"])
    add("Status generation bukan 'generated'", "OK" if not gen_fail.any() else "ERROR", gen_fail.sum())
    cnt = T.groupby(["qid", "method"]).size()
    keys = set(zip(R.qid, R.method))
    empty = [x for x in keys if x not in cnt.index]
    add("Kasus tanpa hasil retrieval (retrieval kosong)", "OK" if not empty else "ERROR", len(empty))
    add(f"Kasus dengan chunk retrieval < k={k}", "INFO", (cnt < k).sum(), "mis. Graph RAG mengembalikan jumlah chunk variabel; lihat Precision@k ketat.")
    extra = set(zip(T.qid, T.method)) - keys
    add("Retrieval tanpa baris di Raw Results", "OK" if not extra else "ERROR", len(extra))
    # label relevansi
    ef = R["expected_files"].map(parse_files)
    add("Pertanyaan tanpa expected source files (label relevansi)", "OK" if ef.map(len).gt(0).all() else "ERROR", (ef.map(len) == 0).sum())
    # golden
    if "golden" in data:
        G = data["golden"]
        gi = G.set_index("qid")
        miss = set(R.qid) - set(gi.index)
        add("Question ID di Raw Results tidak ada di Golden Set", "OK" if not miss else "ERROR", len(miss))
        drift_a = drift_q = drift_d = 0
        for q, g in R.drop_duplicates("qid").set_index("qid").iterrows():
            if q in gi.index:
                x = gi.loc[q]
                drift_a += int(_norm(x["ref_answer"]) != _norm(g["ref_answer"]))
                drift_q += int(_norm(x["question"]) != _norm(g["question"]))
                drift_d += int(str(x["doc"]) != str(g["doc"]))
        add("Jawaban acuan Golden Set != jawaban acuan saat run", "PERINGATAN" if drift_a else "OK", drift_a,
            "Golden Set direvisi setelah sebagian run; analisis memakai acuan yang dipakai saat run (Raw Results).")
        add("Teks pertanyaan Golden Set != teks saat run", "PERINGATAN" if drift_q else "OK", drift_q)
        add("Dokumen target Golden Set != dokumen saat run", "ERROR" if drift_d else "OK", drift_d)
    # kasus
    cases = R.copy()
    cases["dup_flag"] = cases.duplicated(["qid", "method"], keep="last")
    cases["paired"] = cases["qid"].map(piv).fillna(0).ge(2)
    reasons = []
    for i, r in cases.iterrows():
        why = []
        if r["dup_flag"]: why.append("duplikat (versi lebih lama)")
        if not r["paired"]: why.append("tidak ada pasangan metode lain")
        if _to_bool(r["api_ok"]) is False: why.append("API gagal")
        if str(r["status"]) in SYSTEM_FAIL_STATUS: why.append(f"gagal sistem: {r['status']}")
        if (r["qid"], r["method"]) not in cnt.index: why.append("retrieval kosong")
        if not parse_files(r["expected_files"]): why.append("label relevansi tidak tersedia")
        reasons.append("; ".join(why))
    cases["alasan_eksklusi"] = reasons
    cases["valid"] = cases["alasan_eksklusi"].eq("")
    return pd.DataFrame(issues), cases


# --------------------------------------------------------------------------- metrik per kasus
def tokens(s): return set(re.findall(r"\w+", str(s).casefold(), flags=re.UNICODE))


def compute_case_metrics(data, cases, k=K_DEFAULT):
    """Satu baris per kasus VALID (qid, metode). Retrieval, generasi, latency, sumber."""
    T = data["retrieval"].copy(); T["rank"] = pd.to_numeric(T["rank"], errors="coerce")
    ctx = data.get("context"); gold = data.get("golden")
    ev = gold.set_index("qid")["evidence"].to_dict() if gold is not None and "evidence" in gold else {}
    rev = data.get("review")
    prov = set()
    cit = {}
    if rev is not None and len(rev):
        rv = rev.copy(); rv["value"] = pd.to_numeric(rv["value"], errors="coerce")
        prov = set(map(tuple, rv[rv["status"].astype(str).str.contains("perlu konfirmasi", case=False, na=False)][["qid", "method"]].values))
        for (q, m, it), v in rv.groupby(["qid", "method", "item"])["value"].first().items():
            cit[(q, m, it)] = v
    out = []
    for _, c in cases[cases["valid"]].iterrows():
        q, m = c["qid"], c["method"]
        exp = {stem(x) for x in parse_files(c["expected_files"])}
        d = T[(T.qid == q) & (T.method == m)].sort_values("rank").head(k)
        rel = [stem(f) in exp for f in d["file"]] if d["file"].notna().all() and "file" in d else [bool(_to_bool(x)) for x in d["expected_flag"]]
        n = len(rel); nrel = sum(rel)
        docs_ret = list(dict.fromkeys(d["doc"].tolist()))
        rel_docs = [x for x in docs_ret if str(x) == str(c["doc"])]
        row = dict(qid=q, doc=c["doc"], method=m, n_chunks=n, n_rel_chunks=nrel, n_unique_docs=len(docs_ret),
                   precision_chunk=nrel / n if n else np.nan, precision_at_k=nrel / k, hit=int(nrel > 0),
                   mrr=next((1 / i for i, x in enumerate(rel, 1) if x), 0.0),
                   recall_doc=float(len(rel_docs) > 0), precision_doc=len(rel_docs) / len(docs_ret) if docs_ret else np.nan)
        # evidence recall leksikal (opsional): token kutipan bukti yang muncul pada konteks yang dikirim ke LLM
        e = ev.get(q)
        if isinstance(e, str) and e.strip() and ctx is not None and len(ctx):
            tx = " ".join(ctx[(ctx.qid == q) & (ctx.method == m)]["text"].astype(str))
            et = tokens(e); row["evidence_recall"] = len(et & tokens(tx)) / len(et) if et else np.nan
        else: row["evidence_recall"] = np.nan
        # generasi
        status = str(c["status"])
        row["status"] = status
        row["category"] = ("Terjawab" if status == "ANSWERED" else "Sebagian" if status == "PARTIAL"
                           else "Abstain / tidak ditemukan" if status in ABSTAIN_STATUS else "Lainnya")
        row["abstain"] = int(status in ABSTAIN_STATUS)
        for col in ("faith", "corr", "relev", "latency", "latency_server"):
            row[col] = pd.to_numeric(c[col], errors="coerce")
        row["cit_precision"] = cit.get((q, m, "Citation Precision"), np.nan)
        row["cit_coverage"] = cit.get((q, m, "Citation Coverage"), np.nan)
        cd = cited_docs(c["citations"]) if isinstance(c["citations"], str) else None
        row["n_citations"] = len(cd) if cd is not None else np.nan
        row["source_accuracy"] = (sum(x == str(c["doc"]) for x in cd) / len(cd)) if cd else np.nan
        row["correct_bin"] = float(row["corr"] >= CORRECT_MIN) if pd.notna(row["corr"]) else np.nan
        row["provisional"] = int((q, m) in prov)
        row["label_actual"] = (c["label_actual"] if isinstance(c.get("label_actual"), str) and c["label_actual"] in LABELS else
                               (LABELS[0] if row["corr"] >= CORRECT_MIN else LABELS[1] if row["corr"] == PARTIAL_VALUE else LABELS[2])
                               if pd.notna(row["corr"]) else None)
        row["label_pred"] = STATUS_TO_PRED.get(status)
        out.append(row)
    M = pd.DataFrame(out)
    if len(M):
        q3 = M["latency"].quantile(.75); q1 = M["latency"].quantile(.25)
        M["latency_outlier"] = (M["latency"] > q3 + 3 * (q3 - q1)).astype(int)
    return M


METRICS_ORDER = [
    # (kolom, label, arah: +1 lebih tinggi lebih baik, -1 lebih rendah lebih baik, kelompok, jenis)
    ("precision_chunk", "Precision (chunk relevan / chunk diambil)", 1, "Retrieval", "otomatis, berbasis dokumen acuan"),
    ("precision_at_k", "Precision@k ketat (chunk relevan / k)", 1, "Retrieval", "otomatis, berbasis dokumen acuan"),
    ("recall_doc", "Recall@k tingkat dokumen", 1, "Retrieval", "otomatis (=Hit Rate bila 1 dokumen relevan)"),
    ("hit", "Hit Rate@k", 1, "Retrieval", "otomatis"),
    ("mrr", "MRR (rank chunk relevan pertama)", 1, "Retrieval", "otomatis"),
    ("precision_doc", "Precision tingkat dokumen", 1, "Retrieval", "otomatis"),
    ("evidence_recall", "Evidence recall leksikal (konteks LLM)", 1, "Retrieval", "otomatis, proksi leksikal; bukan penilaian semantik"),
    ("faith", "Faithfulness (1-5)", 1, "Generation", "skor review/LLM-judge; abstain dinilai 5 oleh konvensi workbook"),
    ("relev", "Answer Relevancy (1-5)", 1, "Generation", "skor review/LLM-judge"),
    ("corr", "Answer Correctness (1-5)", 1, "Generation", "berbasis jawaban acuan; skor review/LLM-judge"),
    ("correct_bin", f"Proporsi jawaban benar (Correctness >= {CORRECT_MIN})", 1, "Generation", "turunan dari Correctness"),
    ("source_accuracy", "Source accuracy (sitasi dari dokumen acuan)", 1, "Generation", "otomatis dari kolom Sitasi (JSON)"),
    ("cit_precision", "Citation Precision (0-1)", 1, "Generation", "review manual"),
    ("cit_coverage", "Citation Coverage (0-1)", 1, "Generation", "review manual"),
    ("abstain", "Proporsi abstain (NOT_FOUND/UNSUPPORTED)", -1, "Generation", "otomatis dari Status evaluasi"),
    ("latency", "Latency klien (ms)", -1, "Operational", "otomatis; sesi berbeda, tidak dikontrol"),
]
BINARY = ["hit", "recall_doc", "correct_bin", "abstain"]


def aggregate(M):
    rows = []
    for col, label, d, grp, kind in METRICS_ORDER:
        r = dict(kelompok=grp, metrik=label, kolom=col, jenis=kind)
        for m, nm in ((GRAPH, "Graph"), (VECTOR, "Vector")):
            s = M[M.method == m][col].dropna()
            r[f"n_{nm}"] = len(s); r[f"mean_{nm}"] = s.mean() if len(s) else np.nan
            r[f"median_{nm}"] = s.median() if len(s) else np.nan; r[f"sd_{nm}"] = s.std(ddof=1) if len(s) > 1 else np.nan
        rows.append(r)
    return pd.DataFrame(rows)


def answered_only(M):
    """Faithfulness/Relevancy/Correctness hanya pada jawaban yang bukan abstain (menghindari inflasi faithfulness=5 pada abstain)."""
    A = M[M.abstain == 0]
    return pd.DataFrame([dict(metode=m, n=int((A.method == m).sum()),
                              faith=A[A.method == m]["faith"].mean(), relev=A[A.method == m]["relev"].mean(),
                              corr=A[A.method == m]["corr"].mean()) for m in (GRAPH, VECTOR)])


def per_document(M):
    g = M.groupby(["doc", "method"]).agg(n=("qid", "count"), precision_chunk=("precision_chunk", "mean"), precision_at_k=("precision_at_k", "mean"),
                                         hit=("hit", "mean"), mrr=("mrr", "mean"), faith=("faith", "mean"), relev=("relev", "mean"),
                                         corr=("corr", "mean"), correct_bin=("correct_bin", "mean"), abstain=("abstain", "mean"),
                                         latency_median=("latency", "median")).reset_index()
    return g


# --------------------------------------------------------------------------- pasangan & statistik
def paired_wide(M):
    cols = [c for c, *_ in METRICS_ORDER] + ["status", "category", "label_actual", "label_pred", "provisional", "latency_outlier", "n_chunks"]
    W = M.pivot(index=["qid", "doc"], columns="method", values=[c for c in cols if c in M.columns])
    W.columns = [f"{a}|{'G' if b == GRAPH else 'V'}" for a, b in W.columns]
    W = W.reset_index()
    both = W[[c for c in W.columns if c.startswith("n_chunks|")]].notna().all(axis=1)
    return W[both].reset_index(drop=True)


def boot_ci(x, n=5000, seed=42):
    x = np.asarray(x, float)
    if len(x) < 2: return (np.nan, np.nan)
    rng = np.random.default_rng(seed)
    means = rng.choice(x, (n, len(x))).mean(axis=1)
    return tuple(np.percentile(means, [2.5, 97.5]))


def holm(p):
    p = np.asarray(p, float); idx = np.argsort(np.where(np.isnan(p), np.inf, p)); out = np.full(len(p), np.nan); run = 0.0
    m = int((~np.isnan(p)).sum())
    for rank, i in enumerate(idx[:m]):
        run = max(run, (m - rank) * p[i]); out[i] = min(1.0, run)
    return out


def paired_tests(W, alpha=0.05):
    from scipy import stats
    rows = []
    for col, label, d, grp, kind in METRICS_ORDER:
        g, v = f"{col}|G", f"{col}|V"
        if g not in W: continue
        s = W[[g, v]].dropna(); n = len(s)
        r = dict(kelompok=grp, metrik=label, kolom=col, n_pasangan=n, arah="lebih tinggi lebih baik" if d > 0 else "lebih rendah lebih baik")
        if n == 0:
            r.update(catatan="tidak ada pasangan valid"); rows.append(r); continue
        diff = (s[g] - s[v]).to_numpy(float)
        lo, hi = boot_ci(diff)
        r.update(mean_G=s[g].mean(), mean_V=s[v].mean(), mean_diff=diff.mean(), median_diff=float(np.median(diff)), ci95_lo=lo, ci95_hi=hi,
                 G_lebih_tinggi=int((diff > 0).sum()), setara=int((diff == 0).sum()), G_lebih_rendah=int((diff < 0).sum()))
        nz = diff[diff != 0]
        if col in BINARY:
            b = int(((s[g] == 1) & (s[v] == 0)).sum()); c = int(((s[g] == 0) & (s[v] == 1)).sum())
            r.update(uji="McNemar exact", statistik=f"b(G1V0)={b}, c(G0V1)={c}")
            if b + c == 0: r["catatan"] = "tidak ada pasangan diskordan; uji tidak dapat dihitung"
            else:
                r["p_value"] = float(stats.binomtest(min(b, c), b + c, 0.5).pvalue)
                if b + c < 10: r["catatan"] = "diskordan < 10: daya uji rendah"
        else:
            r["uji"] = "Wilcoxon signed-rank"
            if len(nz) < 6: r["catatan"] = f"selisih tidak nol hanya {len(nz)} (< 6): uji tidak diandalkan; gunakan deskriptif"
            else:
                try:
                    w = stats.wilcoxon(diff, zero_method="wilcox", method="auto")
                    r.update(statistik=f"W={w.statistic:.1f}", p_value=float(w.pvalue))
                except Exception as e: r["catatan"] = f"Wilcoxon gagal: {e}"
        rows.append(r)
    T = pd.DataFrame(rows)
    if "p_value" in T: T["p_holm"] = holm(T["p_value"].to_numpy(float))
    return T


def direction(row):
    """+1 = Graph lebih baik, -1 = Vector lebih baik, 0 = setara. Metrik skala memakai MEDIAN selisih (konsisten dengan Wilcoxon);
    bila median 0 dipakai rata-rata. Mengembalikan (arah, konflik_mean_median)."""
    d = {"lebih tinggi lebih baik": 1, "lebih rendah lebih baik": -1}[row["arah"]]
    md, mn = row.get("median_diff"), row.get("mean_diff")
    if pd.isna(mn): return 0, False
    basis = mn if (row["kolom"] in BINARY or md == 0 or pd.isna(md)) else md
    conflict = bool(row["kolom"] not in BINARY and md != 0 and mn != 0 and np.sign(md) != np.sign(mn))
    return int(np.sign(basis) * d), conflict


def verdict(row, alpha=0.05):
    dr, conflict = direction(row)
    if pd.isna(row.get("mean_diff")): return "tidak dapat dinilai"
    if dr == 0: return "setara (selisih 0)"
    who = "Graph RAG" if dr > 0 else "Vector RAG"
    p = row.get("p_holm", np.nan)
    extra = "; PERHATIAN: rata-rata dan median berlawanan arah (dipengaruhi outlier), arah memakai median" if conflict else ""
    if pd.isna(p): return f"arah condong ke {who}, tidak teruji secara inferensial{extra}"
    return (f"{who} lebih baik, signifikan (p Holm={p:.3f}){extra}" if p < alpha else f"arah condong ke {who}, TIDAK signifikan (p Holm={p:.3f}){extra}")


# --------------------------------------------------------------------------- confusion matrix
def retrieval_confusion(M, data, k=K_DEFAULT, universe=None):
    """Tingkat dokumen. Unit: pasangan (pertanyaan, dokumen kandidat). Relevan = dokumen target Golden Set (1 per pertanyaan).
    Himpunan kandidat (universe) sama untuk kedua metode: semua Document ID yang muncul di retrieval kedua metode + dokumen target."""
    T = data["retrieval"]
    if universe is None: universe = sorted(set(T["doc"].astype(str)) | set(M["doc"].astype(str)))
    res = {}
    for m in (GRAPH, VECTOR):
        tp = fp = fn = tn = 0
        for _, r in M[M.method == m].iterrows():
            d = T[(T.qid == r["qid"]) & (T.method == m)].assign(rank=lambda x: pd.to_numeric(x["rank"], errors="coerce")).sort_values("rank").head(k)
            ret = set(d["doc"].astype(str)); rel = {str(r["doc"])}
            tp += len(ret & rel); fp += len(ret - rel); fn += len(rel - ret); tn += len(set(universe) - ret - rel)
        res[m] = dict(TP=tp, FP=fp, FN=fn, TN=tn)
    return res, universe


def cls_metrics(c):
    tp, fp, fn, tn = c["TP"], c["FP"], c["FN"], c["TN"]; dv = lambda a, b: a / b if b else np.nan
    p, rc = dv(tp, tp + fp), dv(tp, tp + fn)
    return dict(Precision=p, Recall=rc, Specificity=dv(tn, tn + fp), F1=dv(2 * p * rc, p + rc) if p == p and rc == rc else np.nan,
                Accuracy=dv(tp + tn, tp + fp + fn + tn))


def answer_confusion(M, only_confirmed=False):
    """Multikelas: label aktual (Correctness manual) x label prediksi (status sistem)."""
    out = {}
    for name, sub in ((GRAPH, M[M.method == GRAPH]), (VECTOR, M[M.method == VECTOR]), ("Gabungan", M)):
        if only_confirmed: sub = sub[sub.provisional == 0]
        s = sub.dropna(subset=["label_actual", "label_pred"])
        cm = pd.crosstab(pd.Categorical(s["label_actual"], LABELS), pd.Categorical(s["label_pred"], LABELS), dropna=False)
        out[name] = cm
    return out


def multiclass_metrics(cm):
    a = cm.to_numpy(); tot = a.sum(); rows = []
    for i, lab in enumerate(LABELS):
        tp = a[i, i]; fp = a[:, i].sum() - tp; fn = a[i, :].sum() - tp; tn = tot - tp - fp - fn
        p = tp / (tp + fp) if tp + fp else 0.0; r = tp / (tp + fn) if tp + fn else 0.0
        rows.append(dict(kelas=lab, TP=tp, FP=fp, FN=fn, TN=tn, Precision=p, Recall=r, F1=2 * p * r / (p + r) if p + r else 0.0, Support=tp + fn))
    df = pd.DataFrame(rows)
    return df, (np.trace(a) / tot if tot else np.nan), df[["Precision", "Recall", "F1"]].mean()


# --------------------------------------------------------------------------- kesimpulan otomatis
def build_findings(M, W, T, cases, issues, k=K_DEFAULT):
    f = []
    nG = int((M.method == GRAPH).sum()); nV = int((M.method == VECTOR).sum()); n = len(W)
    excl = cases[~cases["valid"]]
    f.append(("Cakupan data", f"{len(cases)} baris kasus; {int(cases['valid'].sum())} valid (Graph={nG}, Vector={nV}); {n} pertanyaan berpasangan; "
                              f"{len(excl)} dikecualikan. Kegagalan sistem (API/timeout/error): {int((cases['status'].isin(SYSTEM_FAIL_STATUS) | cases['api_ok'].map(_to_bool).eq(False)).sum())}."))
    ab = M.groupby("method")["abstain"].agg(["sum", "count"])
    f.append(("Abstain vs kegagalan sistem", " ; ".join(f"{m}: {int(ab.loc[m,'sum'])}/{int(ab.loc[m,'count'])} abstain (NOT_FOUND/UNSUPPORTED)" for m in (GRAPH, VECTOR) if m in ab.index) +
              ". Karena seluruh pertanyaan Golden Set memiliki jawaban di korpus, abstain dihitung sebagai kegagalan menjawab, bukan penolakan yang benar."))
    by = {r.kolom: r for r in T.itertuples()}
    def line(col):
        r = by.get(col)
        if r is None or pd.isna(getattr(r, "mean_G", np.nan)): return None
        return f"{r.metrik}: Graph={r.mean_G:.3f}, Vector={r.mean_V:.3f}, selisih={r.mean_diff:+.3f} (CI95 {r.ci95_lo:+.3f}..{r.ci95_hi:+.3f}), n={r.n_pasangan} -> {verdict(T[T.kolom==col].iloc[0])}"
    ret = [line(c) for c in ("precision_chunk", "precision_at_k", "hit", "mrr", "evidence_recall")]
    f.append(("Retrieval", " | ".join(x for x in ret if x)))
    nc = M.groupby("method")["n_chunks"].mean()
    f.append(("Catatan jumlah chunk", f"Rata-rata chunk yang dikembalikan: Graph={nc.get(GRAPH, float('nan')):.2f}, Vector={nc.get(VECTOR, float('nan')):.2f} (k={k}). Precision@k ketat dipengaruhi jumlah chunk yang dikembalikan, bukan hanya ketepatan; Precision per chunk dan Hit/MRR tidak terpengaruh denominator tetap."))
    gen = [line(c) for c in ("corr", "correct_bin", "faith", "relev", "source_accuracy", "abstain")]
    f.append(("Kualitas jawaban", " | ".join(x for x in gen if x)))
    f.append(("Latency", (line("latency") or "tidak tersedia") + f" | median Graph={M[M.method==GRAPH]['latency'].median():.0f} ms, Vector={M[M.method==VECTOR]['latency'].median():.0f} ms; "
                          f"outlier ekstrem: {int(M['latency_outlier'].sum())} kasus. Run dilakukan pada banyak sesi tanpa kontrol beban/cold start, sehingga latency bersifat indikatif."))
    sig = T[(T.get("p_holm", pd.Series(dtype=float)) < 0.05)]
    sup = [x["metrik"] for _, x in sig.iterrows() if direction(x)[0] > 0]
    opp = [x["metrik"] for _, x in sig.iterrows() if direction(x)[0] < 0]
    f.append(("Metrik yang mendukung Graph RAG (signifikan, Holm)", "; ".join(sup) or "tidak ada"))
    f.append(("Metrik yang mendukung Vector RAG (signifikan, Holm)", "; ".join(opp) or "tidak ada"))
    mixed = [r.metrik for r in T.itertuples() if not pd.isna(getattr(r, "mean_diff", np.nan)) and r.metrik not in sup + opp]
    f.append(("Selisih tidak signifikan / tidak teruji", "; ".join(mixed) or "tidak ada"))
    if n:
        c = W["corr|G"] - W["corr|V"]
        f.append(("Kasus per pertanyaan (Answer Correctness)", f"Graph lebih tinggi pada {int((c>0).sum())}, setara {int((c==0).sum())}, lebih rendah {int((c<0).sum())} dari {n} pertanyaan."))
    prov = int(M["provisional"].sum())
    f.append(("Kualitas label", f"{prov} kasus (dari {len(M)}) bernilai provisional ('dinilai Claude; perlu konfirmasi evaluator'). Sensitivitas hanya-evaluator disediakan pada confusion matrix jawaban."))
    return f


LIMITATIONS = [
    "Relevansi retrieval berbasis dokumen (file sumber sama dengan expected_source_files), bukan relevansi chunk. Evidence recall leksikal hanyalah proksi tambahan.",
    "Setiap pertanyaan hanya memiliki 1 dokumen relevan sehingga Recall@k tingkat dokumen identik dengan Hit Rate@k; keduanya tidak independen.",
    "Pertanyaan tersarang dalam 5 dokumen (15 per dokumen) sehingga tidak sepenuhnya independen; uji berpasangan per pertanyaan dapat terlalu optimistis. Lihat hasil per dokumen.",
    "Skor Faithfulness/Relevancy/Correctness/Citation berasal dari review satu penilai dan/atau LLM-judge tanpa uji antar-penilai (mis. Cohen's kappa). Sebagian kasus berstatus provisional.",
    "Konvensi workbook memberi abstain Faithfulness=5, Correctness=1, Relevancy=3. Faithfulness gabungan karena itu cenderung menguntungkan metode yang lebih sering abstain; lihat tabel 'hanya jawaban non-abstain'.",
    "Pada confusion matrix jawaban, kasus abstain otomatis berlabel aktual 'salah' (konvensi Correctness=1), sehingga Precision kelas 'Tidak terjawab / salah' = 1 bersifat sirkular dan tidak boleh dibaca sebagai kualitas sistem; kelas 'benar' dan 'sebagian' lebih informatif.",
    "Graph RAG mengembalikan chunk lebih sedikit dari k=5 pada banyak kasus; Precision (chunk relevan/chunk diambil) dan Precision@k ketat (relevan/k) dilaporkan terpisah.",
    "Golden Set direvisi setelah sebagian run; kondisi pengujian antar sesi tidak seragam (versi pertanyaan/jawaban acuan, waktu, beban). Hanya dua metode pada pertanyaan yang sama di sesi yang sama yang dibandingkan.",
    "Latency diukur dari klien pada banyak sesi, termasuk panggilan LLM eksternal, tanpa kontrol cold start/rate limit; gunakan median dan perlakukan sebagai indikatif.",
    "Hanya korpus Notetaker (5 dokumen, 75 pertanyaan) dan satu LLM; hasil tidak dapat digeneralisasi ke korpus lain tanpa pengujian tambahan.",
    "Hasil menunjukkan asosiasi pada data tersedia; tidak membuktikan mekanisme kausal mengapa suatu metode unggul.",
]


# --------------------------------------------------------------------------- grafik
def make_figures(M, W, T, cm_ret, cms, k=K_DEFAULT):
    import matplotlib; import matplotlib.pyplot as plt
    figs = {}; C = {GRAPH: "#1f6f8b", VECTOR: "#e07a1f"}
    nG, nV = (M.method == GRAPH).sum(), (M.method == VECTOR).sum()
    sub = f"n: Graph={nG}, Vector={nV}"
    def bars(ax, cols, labels, title, ylim=None):
        x = np.arange(len(cols)); w = .38
        for i, m in enumerate((GRAPH, VECTOR)):
            vals = [M[M.method == m][c].mean() for c in cols]; ns = [M[M.method == m][c].notna().sum() for c in cols]
            b = ax.bar(x + (i - .5) * w, vals, w, label=m, color=C[m])
            for rect, v, nn in zip(b, vals, ns): ax.text(rect.get_x() + rect.get_width() / 2, (v if v == v else 0) + (ylim[1] * .01 if ylim else .01), f"{v:.2f}\n(n={nn})", ha="center", va="bottom", fontsize=7)
        ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=8); ax.set_title(title, fontsize=10)
        if ylim: ax.set_ylim(*ylim)
        ax.legend(fontsize=8)
    f, ax = plt.subplots(figsize=(9, 4)); bars(ax, ["precision_chunk", "precision_at_k", "hit", "mrr", "evidence_recall"], ["Precision\n(per chunk)", f"Precision@{k}\nketat", "Hit Rate@k\n(=Recall doc)", "MRR", "Evidence\nrecall"], f"Retrieval - skala 0-1 ({sub})", (0, 1.2)); figs["retrieval"] = f
    f, axs = plt.subplots(1, 2, figsize=(11, 4)); bars(axs[0], ["faith", "relev", "corr"], ["Faithfulness", "Answer\nRelevancy", "Answer\nCorrectness"], f"Semua kasus, skala 1-5 ({sub})", (0, 6.5))
    A = M[M.abstain == 0]; nGa, nVa = (A.method == GRAPH).sum(), (A.method == VECTOR).sum()
    for i, m in enumerate((GRAPH, VECTOR)):
        vals = [A[A.method == m][c].mean() for c in ("faith", "relev", "corr")]; x = np.arange(3); b = axs[1].bar(x + (i - .5) * .38, vals, .38, label=m, color=C[m])
        for r, v in zip(b, vals): axs[1].text(r.get_x() + r.get_width() / 2, v + .05, f"{v:.2f}", ha="center", fontsize=8)
    axs[1].set_xticks(range(3)); axs[1].set_xticklabels(["Faithfulness", "Answer\nRelevancy", "Answer\nCorrectness"], fontsize=8); axs[1].set_ylim(0, 6.5)
    axs[1].set_title(f"Hanya non-abstain (n: Graph={nGa}, Vector={nVa})", fontsize=10); axs[1].legend(fontsize=8); figs["generation"] = f
    f, axs = plt.subplots(1, 2, figsize=(10, 4))
    axs[0].boxplot([M[M.method == m]["latency"].dropna() / 1000 for m in (GRAPH, VECTOR)], labels=[f"{GRAPH}\n(n={nG})", f"{VECTOR}\n(n={nV})"], showfliers=True)
    axs[0].set_ylabel("detik"); axs[0].set_title("Latency klien (linier, outlier ditampilkan)", fontsize=10)
    axs[1].boxplot([M[M.method == m]["latency"].dropna() / 1000 for m in (GRAPH, VECTOR)], labels=[GRAPH, VECTOR]); axs[1].set_yscale("log"); axs[1].set_title("Latency (skala log)", fontsize=10); figs["latency"] = f
    D = per_document(M); docs = sorted(D["doc"].unique())
    f, axs = plt.subplots(1, 3, figsize=(14, 4))
    for ax, (col, ttl, yl) in zip(axs, (("precision_chunk", "Precision (chunk)", (0, 1.15)), ("mrr", "MRR", (0, 1.15)), ("corr", "Answer Correctness (1-5)", (0, 6)))):
        x = np.arange(len(docs))
        for i, m in enumerate((GRAPH, VECTOR)):
            d = D[D.method == m].set_index("doc").reindex(docs); ax.bar(x + (i - .5) * .38, d[col], .38, color=C[m], label=m)
            for xi, v, nn in zip(x + (i - .5) * .38, d[col], d["n"]): ax.text(xi, (v if v == v else 0) + .02, f"n={0 if nn!=nn else int(nn)}", ha="center", fontsize=6, rotation=90)
        ax.set_xticks(x); ax.set_xticklabels(docs, fontsize=8); ax.set_title(ttl, fontsize=10); ax.set_ylim(*yl); ax.legend(fontsize=7)
    figs["per_dokumen"] = f
    f, ax = plt.subplots(figsize=(8, 4)); cats = ["Terjawab", "Sebagian", "Abstain / tidak ditemukan", "Lainnya"]; col = ["#2e8b57", "#e6b800", "#c0392b", "#7f8c8d"]
    for j, m in enumerate((GRAPH, VECTOR)):
        left = 0; s = M[M.method == m]["category"].value_counts()
        for cat, cc in zip(cats, col):
            v = int(s.get(cat, 0)); ax.barh(j, v, left=left, color=cc, label=cat if j == 0 else None)
            if v: ax.text(left + v / 2, j, str(v), ha="center", va="center", color="white", fontsize=9)
            left += v
    ax.set_yticks([0, 1]); ax.set_yticklabels([f"{GRAPH} (n={nG})", f"{VECTOR} (n={nV})"]); ax.legend(fontsize=7, loc="lower right"); ax.set_title("Distribusi status (tidak ada kegagalan sistem jika 'Lainnya'=0)", fontsize=10); figs["status"] = f
    def heat(ax, a, rl, cl, title):
        im = ax.imshow(a, cmap="Blues"); ax.set_xticks(range(a.shape[1])); ax.set_yticks(range(a.shape[0]))
        ax.set_xticklabels(cl, fontsize=7, rotation=20); ax.set_yticklabels(rl, fontsize=7); ax.set_title(title, fontsize=9)
        for i in range(a.shape[0]):
            for j in range(a.shape[1]): ax.text(j, i, int(a[i, j]), ha="center", va="center", color="white" if a[i, j] > a.max() / 2 else "black")
    f, axs = plt.subplots(1, 2, figsize=(9, 4))
    for ax, m in zip(axs, (GRAPH, VECTOR)):
        c = cm_ret[m]; heat(ax, np.array([[c["TP"], c["FN"]], [c["FP"], c["TN"]]]), ["Relevan", "Tidak relevan"], ["Diambil", "Tidak diambil"], f"{m} - dokumen (k={k})")
    figs["cm_retrieval"] = f
    f, axs = plt.subplots(1, 2, figsize=(12, 4.5))
    for ax, m in zip(axs, (GRAPH, VECTOR)):
        cm = cms[m]; heat(ax, cm.to_numpy(), [l.replace(" / ", "/\n") for l in LABELS], [l.replace(" / ", "/\n") for l in LABELS], f"{m} (n={int(cm.to_numpy().sum())})\nbaris=aktual (Correctness), kolom=prediksi (status)")
    figs["cm_answer"] = f
    f, axs = plt.subplots(1, 2, figsize=(11, 4))
    if len(W):
        dc = (W["corr|G"] - W["corr|V"]); vals = sorted(dc.unique()); axs[0].bar([str(int(v)) for v in vals], [int((dc == v).sum()) for v in vals], color=["#c0392b" if v < 0 else "#7f8c8d" if v == 0 else "#1f6f8b" for v in vals])
        axs[0].set_title(f"Selisih Answer Correctness (Graph - Vector), n={len(W)} pasangan", fontsize=9); axs[0].set_xlabel("selisih skor"); axs[0].set_ylabel("jumlah pertanyaan")
        dl = ((W["latency|G"] - W["latency|V"]) / 1000).dropna(); axs[1].hist(dl, bins=25, color="#555"); axs[1].axvline(0, color="r"); axs[1].set_title(f"Selisih latency detik (Graph - Vector), n={len(dl)}", fontsize=9)
    figs["paired"] = f
    for fg in figs.values(): fg.tight_layout()
    return figs


# --------------------------------------------------------------------------- ekspor workbook
def build_workbook(path, data, M, W, T, cases, issues, D, cm_ret, cms, cms_conf, A_only, findings, golden_df, k=K_DEFAULT, use_formulas=True, source_name=""):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter as L
    NAVY, PALE = "17365D", "F3F6FA"; thin = Side(style="thin", color="D9E1F2")
    F = "Arial"
    wb = Workbook(); wb.remove(wb.active)
    def sheet(name, tab):
        ws = wb.create_sheet(name); ws.sheet_properties.tabColor = tab; ws.sheet_view.showGridLines = False; return ws
    def hdr(ws, row, vals, col=1):
        for j, v in enumerate(vals):
            c = ws.cell(row, col + j, v); c.fill = PatternFill("solid", fgColor=NAVY); c.font = Font(name=F, bold=True, color="FFFFFF", size=10); c.alignment = Alignment(wrap_text=True, vertical="center")
    def title(ws, row, text, size=12): ws.cell(row, 1, text).font = Font(name=F, bold=True, size=size, color=NAVY)
    def clean(v):
        if v is None: return None
        if isinstance(v, (np.integer,)): return int(v)
        if isinstance(v, (np.floating,)): return None if np.isnan(v) else float(v)
        if isinstance(v, float) and math.isnan(v): return None
        if isinstance(v, str): return "".join(ch for ch in v if ch in "\t\n\r" or ord(ch) >= 32)[:32000]
        return v
    def dump(ws, df, widths=None, start=1):
        hdr(ws, start, list(df.columns))
        for i, row in enumerate(df.itertuples(index=False), start + 1):
            for j, v in enumerate(row, 1):
                c = ws.cell(i, j, clean(v)); c.font = Font(name=F, size=9); c.alignment = Alignment(vertical="top", wrap_text=isinstance(v, str) and len(v) > 40)
        ws.freeze_panes = ws.cell(start + 1, 1)
        for j, cname in enumerate(df.columns, 1): ws.column_dimensions[L(j)].width = (widths or {}).get(cname, min(max(12, len(str(cname)) + 2), 42))
        if len(df): ws.auto_filter.ref = f"A{start}:{L(len(df.columns))}{start + len(df)}"
    def body(ws, text, row, col=1, bold=False, wrap=True, width=None):
        c = ws.cell(row, col, text); c.font = Font(name=F, size=10, bold=bold); c.alignment = Alignment(wrap_text=wrap, vertical="top")
        return c

    n_pairs = len(W); nG = int((M.method == GRAPH).sum()); nV = int((M.method == VECTOR).sum())
    # ---------------- README
    ws = sheet("README", "17365D"); ws.column_dimensions["A"].width = 30; ws.column_dimensions["B"].width = 120
    title(ws, 1, "ARCANA - Evaluasi Graph RAG vs Vector RAG (korpus Notetaker)", 14)
    meta = [("Tujuan", "Menguji apakah Graph RAG memberi hasil lebih baik daripada Vector RAG pada knowledge base ARCANA, memakai pertanyaan, dokumen target, dan jawaban acuan yang sama (desain berpasangan)."),
            ("Cakupan", "Kualitas retrieval, relevansi konteks, kualitas jawaban, ketepatan sumber, dan efisiensi pemrosesan (latency). SUS dan audit/traceability TIDAK termasuk dalam evaluasi."),
            ("Sumber data", source_name or "workbook hasil pengujian"), ("Unit analisis", f"Pasangan (Question ID, Metode). Pasangan berpasangan = Question ID yang sama pada kedua metode. n kasus valid: Graph={nG}, Vector={nV}; n pertanyaan berpasangan={n_pairs}. k={k}."),
            ("Prinsip", "Data mentah tidak diubah. Sheet RAW_* adalah salinan apa adanya; sheet analisis dihitung ulang dari data tersebut. Kegagalan sistem dibedakan dari abstain (NOT_FOUND/UNSUPPORTED_ANSWER). Tidak ada nilai kosong yang diisi 0 atau 100."),
            ("Peta sheet", "ANALISIS: Golden Set | Retrieval Metrics | Generation Metrics | Comparison Matrix | Summary & Findings.  DATA MENTAH: Raw Results | Raw Retrieval | Raw LLM Context | Raw Trace | Manual Review | Run History | Run Config.  Sheet lama yang digantikan: Ringkasan, Matriks Metrik, Detail Evaluasi, Confusion Matrix, Ringkasan Metrik, Keterangan (turunan; dihitung ulang), Survei SUS, Pertanyaan SUS (dihapus), Log Error (kosong).")]
    r = 3
    for a, b in meta: body(ws, a, r, bold=True); body(ws, b, r, 2); r += 1
    r += 1; title(ws, r, "Definisi metrik"); r += 1; hdr(ws, r, ["Metrik", "Definisi dan metode"]); hdr(ws, r, ["Jenis"], 3); ws.column_dimensions["C"].width = 40; r += 1
    defs = {"precision_chunk": "chunk dari dokumen acuan / jumlah chunk yang diambil (top-k, maks k).", "precision_at_k": "chunk dari dokumen acuan / k (denominator tetap k=5; menghukum metode yang mengembalikan < k chunk).",
            "recall_doc": "dokumen relevan unik yang ditemukan / dokumen relevan (1 per pertanyaan).", "hit": "1 bila minimal satu chunk dari dokumen acuan ada pada top-k, selain itu 0; rata-rata antar pertanyaan.",
            "mrr": "1 / rank chunk relevan pertama pada top-k; 0 bila tidak ada.", "precision_doc": "dokumen acuan / jumlah dokumen unik pada top-k.",
            "evidence_recall": "fraksi token kutipan bukti Golden Set yang muncul pada teks konteks yang dikirim ke LLM (leksikal; hanya bila Golden Set & Raw LLM Context tersedia).",
            "faith": "skor 1-5 dukungan jawaban oleh konteks (review/LLM-judge). Abstain=5 menurut konvensi workbook.", "relev": "skor 1-5 relevansi jawaban terhadap pertanyaan.",
            "corr": "skor 1-5 kesesuaian jawaban dengan jawaban acuan.", "correct_bin": f"1 bila Answer Correctness >= {CORRECT_MIN}.",
            "source_accuracy": "sitasi yang doc_id-nya sama dengan dokumen target / seluruh sitasi (kosong bila tidak ada sitasi).",
            "cit_precision": "sitasi yang benar-benar mendukung klaim / seluruh sitasi (review manual; kosong untuk abstain).", "cit_coverage": "klaim faktual yang bersitasi / seluruh klaim faktual (review manual).",
            "abstain": "Status evaluasi NOT_FOUND atau UNSUPPORTED_ANSWER.", "latency": "waktu request sisi klien (ms), diagregasi dengan rata-rata dan median."}
    for col, label, d, grp, kind in METRICS_ORDER:
        body(ws, label, r, bold=True); body(ws, defs.get(col, ""), r, 2); body(ws, kind, r, 3); r += 1
    r += 1; title(ws, r, "Cara membaca hasil"); r += 1
    for t in ["Mulai dari Summary & Findings (kesimpulan dan keterbatasan), lalu Comparison Matrix (per pertanyaan), Retrieval Metrics dan Generation Metrics (agregat, per dokumen, confusion matrix).",
              "Signifikansi: Wilcoxon signed-rank (metrik skala) dan McNemar exact (biner), p-value dikoreksi Holm lintas metrik. Selisih = Graph - Vector.",
              "Confusion matrix retrieval bersifat tingkat dokumen dengan himpunan kandidat identik untuk kedua metode (lihat Retrieval Metrics). Confusion matrix jawaban membandingkan status sistem dengan label aktual dari Answer Correctness."]:
        body(ws, t, r); ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2); ws.row_dimensions[r].height = 32; r += 1

    # ---------------- Golden Set
    ws = sheet("Golden Set", "2E8B57")
    g = golden_df.copy()
    rr = data["results"].drop_duplicates("qid", keep="last").set_index("qid")
    g["Acuan saat run sama dengan Golden Set?"] = [("Ya" if q in rr.index and _norm(rr.loc[q, "ref_answer"]) == _norm(a) and _norm(rr.loc[q, "question"]) == _norm(qq) else "TIDAK (Golden Set direvisi setelah run)" if q in rr.index else "tidak ada di Raw Results")
                                                  for q, a, qq in zip(g["qid"], g["ref_answer"], g["question"])]
    g["Label relevansi"] = "Dokumen relevan = " + g["doc"].astype(str) + " (file di expected_source_files)"
    g = g.rename(columns={"qid": "Question ID", "doc": "Document ID", "question": "Pertanyaan", "ref_answer": "Jawaban acuan", "expected_files": "Expected source files", "evidence": "Evidence quote"})
    dump(ws, g, {"Pertanyaan": 60, "Jawaban acuan": 60, "Expected source files": 40, "Evidence quote": 50, "Acuan saat run sama dengan Golden Set?": 30, "Label relevansi": 34})

    # ---------------- Raw sheets (data asli apa adanya, nama kolom asli)
    for key, nm in (("results", "Raw Results"), ("retrieval", "Raw Retrieval"), ("context", "Raw LLM Context"), ("review", "Manual Review"),
                    ("trace", "Raw Trace"), ("history", "Run History"), ("config", "Run Config")):
        if key in data["raw"]:
            ws = sheet(nm, "7F7F7F"); df = data["raw"][key].copy()   # data asli apa adanya, semua kolom asli
            for c in df.columns:
                df[c] = df[c].map(lambda x: bool(x) if isinstance(x, np.bool_) else x)
            dump(ws, df)

    # ---------------- Retrieval Metrics
    ws = sheet("Retrieval Metrics", "1F6F8B"); ws.column_dimensions["A"].width = 46
    for j in range(2, 14): ws.column_dimensions[L(j)].width = 15
    title(ws, 1, f"A. Retrieval Evaluation (k={k}) - satuan: pertanyaan per metode"); body(ws, "Rata-rata dihitung dari tabel per-pertanyaan (bagian D) dengan rumus AVERAGEIFS. Selisih = Graph - Vector.", 2, wrap=False)
    ret_cols = [c for c in ("precision_chunk", "precision_at_k", "recall_doc", "hit", "mrr", "precision_doc", "evidence_recall")]
    lab = {c: l for c, l, *_ in METRICS_ORDER}
    # susun posisi: A tabel agregat (baris 4..), B per dokumen, C confusion, D per-pertanyaan
    rowA = 4; rowB = rowA + len(ret_cols) + 4; docs = sorted(M.doc.unique()); rowC = rowB + 3 + len(docs) * 2 + 1; rowD = rowC + 18
    pqc = ["qid", "doc", "method", "n_chunks", "n_rel_chunks"] + ret_cols
    pq = M[pqc].sort_values(["qid", "method"]).reset_index(drop=True)
    colpos = {c: j for j, c in enumerate(pqc, 1)}
    first, last = rowD + 1, rowD + len(pq)
    hdr(ws, rowA, ["Metrik", f"Graph RAG", "Vector RAG", "Selisih (G-V)", "n Graph", "n Vector"])
    for i, c in enumerate(ret_cols, rowA + 1):
        ws.cell(i, 1, lab[c]).font = Font(name=F, size=10)
        for j, m in ((2, GRAPH), (3, VECTOR)):
            rng = f"${L(colpos[c])}${first}:${L(colpos[c])}${last}"; mr = f"$C${first}:$C${last}"
            ws.cell(i, j, f'=IFERROR(AVERAGEIFS({rng},{mr},"{m}"),"")' if use_formulas else clean(M[M.method == m][c].mean())).number_format = "0.000"
            ws.cell(i, 5 if j == 2 else 6, f'=COUNTIFS({mr},"{m}",{rng},"<>")' if use_formulas else int(M[M.method == m][c].notna().sum()))
        ws.cell(i, 4, f'=IFERROR(B{i}-C{i},"")' if use_formulas else clean((M[M.method == GRAPH][c].mean() - M[M.method == VECTOR][c].mean()))).number_format = "+0.000;-0.000;0.000"
    body(ws, f"Catatan: Recall@k tingkat dokumen = Hit Rate@k karena tepat 1 dokumen relevan per pertanyaan. Evidence recall kosong bila Golden Set/Raw LLM Context tidak tersedia.", rowA + len(ret_cols) + 1, wrap=False)
    title(ws, rowB, "B. Hasil per dokumen (rata-rata per dokumen; n = pertanyaan)"); hdr(ws, rowB + 1, ["Dokumen", "Metode", "n", "Precision (chunk)", "Precision@k ketat", "Hit Rate", "MRR"])
    r = rowB + 2
    for d in docs:
        for m in (GRAPH, VECTOR):
            s = M[(M.doc == d) & (M.method == m)]
            for j, v in enumerate([d, m, len(s), s.precision_chunk.mean(), s.precision_at_k.mean(), s.hit.mean(), s.mrr.mean()], 1):
                c = ws.cell(r, j, clean(v)); c.font = Font(name=F, size=9)
                if j > 3: c.number_format = "0.000"
            r += 1
    title(ws, rowC, "C. Confusion matrix retrieval - tingkat dokumen (jumlah gabungan seluruh pertanyaan)")
    body(ws, f"TP=dokumen relevan terambil; FP=dokumen tidak relevan terambil; FN=dokumen relevan tidak terambil; TN=dokumen kandidat tidak relevan yang tidak terambil. Himpunan kandidat identik untuk kedua metode: {len(_UNIVERSE)} dokumen (semua Document ID yang muncul pada retrieval + dokumen target).", rowC + 1, wrap=False)
    hdr(ws, rowC + 2, ["Metode", "TP", "FP", "FN", "TN", "Precision", "Recall", "Specificity", "F1", "Accuracy"])
    for i, m in enumerate((GRAPH, VECTOR), rowC + 3):
        c = cm_ret[m]; ws.cell(i, 1, m)
        for j, key in enumerate(("TP", "FP", "FN", "TN"), 2): ws.cell(i, j, c[key])
        if use_formulas:
            ws.cell(i, 6, f'=IFERROR(B{i}/(B{i}+C{i}),"")'); ws.cell(i, 7, f'=IFERROR(B{i}/(B{i}+D{i}),"")'); ws.cell(i, 8, f'=IFERROR(E{i}/(E{i}+C{i}),"")')
            ws.cell(i, 9, f'=IFERROR(2*F{i}*G{i}/(F{i}+G{i}),"")'); ws.cell(i, 10, f'=IFERROR((B{i}+E{i})/(B{i}+C{i}+D{i}+E{i}),"")')
        else:
            cm_ = cls_metrics(c)
            for j, key in zip(range(6, 11), ("Precision", "Recall", "Specificity", "F1", "Accuracy")): ws.cell(i, j, clean(cm_[key]))
        for j in range(6, 11): ws.cell(i, j).number_format = "0.000"
    body(ws, "Catatan: TN bergantung pada definisi himpunan kandidat; Specificity/Accuracy tingkat dokumen perlu dibaca hati-hati (kandidat sedikit).", rowC + 5, wrap=False)
    title(ws, rowD - 1, "D. Tabel per pertanyaan (sumber rumus bagian A)")
    names = {"qid": "Question ID", "doc": "Document ID", "method": "Metode", "n_chunks": "Chunk diambil (<=k)", "n_rel_chunks": "Chunk relevan"}
    names.update({c: lab[c] for c in ret_cols})
    hdr(ws, rowD, [names[c] for c in pqc])
    for i, row in enumerate(pq.itertuples(index=False), rowD + 1):
        for j, v in enumerate(row, 1):
            c = ws.cell(i, j, clean(v)); c.font = Font(name=F, size=9)
            if j > 5: c.number_format = "0.000"
    ws.freeze_panes = "B4"

    # ---------------- Generation Metrics
    ws = sheet("Generation Metrics", "1F6F8B"); ws.column_dimensions["A"].width = 52
    for j in range(2, 22): ws.column_dimensions[L(j)].width = 15
    gen_cols = ["faith", "relev", "corr", "correct_bin", "source_accuracy", "cit_precision", "cit_coverage", "abstain", "latency"]
    title(ws, 1, "B. Generation Evaluation + efisiensi - satuan: pertanyaan per metode")
    body(ws, "Skor 1-5 berasal dari Raw Results/Manual Review (penilaian manual evaluator, sebagian provisional 'dinilai Claude'), BUKAN metrik otomatis murni. source_accuracy & abstain & latency otomatis. Tidak ada nilai kosong yang diisi.", 2, wrap=False)
    gA = 4; gB = gA + len(gen_cols) + 4; gC = gB + 6; gD = gC + 22; gE = gD + 3 * 7 + 8; gT = gE + 3
    pqg = ["qid", "doc", "method", "status", "category", "provisional"] + gen_cols
    pg = M[pqg].sort_values(["qid", "method"]).reset_index(drop=True); cp = {c: j for j, c in enumerate(pqg, 1)}
    f1, l1 = gT + 1, gT + len(pg)
    hdr(ws, gA, ["Metrik", "Graph RAG", "Vector RAG", "Selisih (G-V)", "n Graph", "n Vector", "Median Graph", "Median Vector"])
    for i, c in enumerate(gen_cols, gA + 1):
        ws.cell(i, 1, lab[c]).font = Font(name=F, size=10); rng = f"${L(cp[c])}${f1}:${L(cp[c])}${l1}"; mr = f"$C${f1}:$C${l1}"
        for j, m in ((2, GRAPH), (3, VECTOR)):
            ws.cell(i, j, f'=IFERROR(AVERAGEIFS({rng},{mr},"{m}"),"")' if use_formulas else clean(M[M.method == m][c].mean())).number_format = "0.000"
            ws.cell(i, 5 if j == 2 else 6, f'=COUNTIFS({mr},"{m}",{rng},"<>")' if use_formulas else int(M[M.method == m][c].notna().sum()))
        ws.cell(i, 4, f'=IFERROR(B{i}-C{i},"")' if use_formulas else clean(M[M.method == GRAPH][c].mean() - M[M.method == VECTOR][c].mean())).number_format = "+0.000;-0.000;0.000"
        ws.cell(i, 7, clean(M[M.method == GRAPH][c].median())); ws.cell(i, 8, clean(M[M.method == VECTOR][c].median()))
    body(ws, "Latency dalam ms. Median disertakan karena distribusi latency miring (outlier).", gA + len(gen_cols) + 1, wrap=False)
    title(ws, gB, "Faithfulness/Relevancy/Correctness hanya pada jawaban non-abstain (menghindari inflasi akibat konvensi abstain)")
    hdr(ws, gB + 1, ["Metode", "n non-abstain", "Faithfulness", "Answer Relevancy", "Answer Correctness"])
    for i, row in enumerate(A_only.itertuples(index=False), gB + 2):
        for j, v in enumerate(row, 1): ws.cell(i, j, clean(v)).number_format = "0.000" if j > 2 else "General"
    title(ws, gC, "Distribusi status (jumlah kasus)")
    cats = ["Terjawab", "Sebagian", "Abstain / tidak ditemukan", "Lainnya"]; hdr(ws, gC + 1, ["Metode", "ANSWERED", "PARTIAL", "NOT_FOUND", "UNSUPPORTED_ANSWER", "Gagal sistem (API/timeout/error)", "Total"])
    for i, m in enumerate((GRAPH, VECTOR), gC + 2):
        s = cases[(cases.method == m)]
        fails = int((s.status.isin(SYSTEM_FAIL_STATUS) | s.api_ok.map(_to_bool).eq(False)).sum())
        vals = [m] + [int((s.status == x).sum()) for x in ("ANSWERED", "PARTIAL", "NOT_FOUND", "UNSUPPORTED_ANSWER")] + [fails]
        for j, v in enumerate(vals, 1): ws.cell(i, j, v)
        ws.cell(i, 7, f"=SUM(B{i}:F{i})" if use_formulas else sum(vals[1:]))
    body(ws, "Abstain (NOT_FOUND/UNSUPPORTED_ANSWER) = sistem berjalan tetapi menyatakan jawaban tidak ditemukan; bukan kegagalan sistem. Karena jawaban selalu ada di korpus, abstain dihitung sebagai kegagalan menjawab.", gC + 4, wrap=False)
    title(ws, gC + 6, "Confusion matrix jawaban (baris = label aktual dari Answer Correctness; kolom = prediksi dari status sistem)")
    body(ws, f"Aktual: Correctness >= {CORRECT_MIN} 'Terjawab benar', = {PARTIAL_VALUE} 'Terjawab sebagian', <= {PARTIAL_VALUE-1} 'Tidak terjawab / salah'. Prediksi: ANSWERED, PARTIAL, NOT_FOUND/UNSUPPORTED_ANSWER.", gC + 7, wrap=False)
    r = gC + 8
    for nm in (GRAPH, VECTOR):
        cm = cms[nm]; hdr(ws, r, [f"{nm} (n={int(cm.to_numpy().sum())})"] + LABELS); 
        for i, lbl in enumerate(LABELS, r + 1):
            ws.cell(i, 1, lbl)
            for j, v in enumerate(cm.loc[lbl].tolist(), 2): ws.cell(i, j, int(v))
        _, acc, mac = multiclass_metrics(cm); ws.cell(r + 4, 1, f"Accuracy={acc:.3f}; macro-F1={mac['F1']:.3f}"); r += 6
    gD = r + 1
    title(ws, gD, "Sensitivitas: hanya label yang dikonfirmasi evaluator (tanpa kasus provisional)")
    r = gD + 1
    for nm in (GRAPH, VECTOR):
        cm = cms_conf[nm]; _, acc, mac = multiclass_metrics(cm)
        ws.cell(r, 1, f"{nm}: n={int(cm.to_numpy().sum())}, Accuracy={acc:.3f}, macro-F1={mac['F1']:.3f}"); r += 1
    title(ws, gT - 1, "C. Tabel per pertanyaan (sumber rumus bagian A)")
    gnames = {"qid": "Question ID", "doc": "Document ID", "method": "Metode", "status": "Status evaluasi", "category": "Kategori", "provisional": "Skor provisional (1=ya)"}; gnames.update({c: lab[c] for c in gen_cols})
    hdr(ws, gT, [gnames[c] for c in pqg])
    for i, row in enumerate(pg.itertuples(index=False), gT + 1):
        for j, v in enumerate(row, 1): ws.cell(i, j, clean(v)).font = Font(name=F, size=9)
    ws.freeze_panes = "B4"

    # ---------------- Comparison Matrix
    ws = sheet("Comparison Matrix", "7B3F98")
    cmc = [("hit", "Hit@k"), ("mrr", "MRR"), ("precision_chunk", "Precision (chunk)"), ("precision_at_k", "Precision@k ketat"), ("corr", "Correctness"), ("faith", "Faithfulness"), ("relev", "Relevancy"), ("latency", "Latency (ms)")]
    cols = ["Question ID", "Document ID", "Status Graph", "Status Vector"]
    for c, l in cmc: cols += [f"{l} Graph", f"{l} Vector", f"{l} Selisih"]
    cols += ["Hasil Correctness", "Hasil Retrieval (MRR)", "Catatan data"]
    ws.cell(1, 1, "Comparison Matrix - pertanyaan sama, kedua metode (Selisih = Graph - Vector; latency: negatif = Graph lebih cepat)").font = Font(name=F, bold=True, size=12, color=NAVY)
    hdr(ws, 3, cols)
    corr_col = 5 + 3 * 4; corr_col_G = 5 + 3 * [c for c, _ in cmc].index("corr"); mrr_G = 5 + 3 * [c for c, _ in cmc].index("mrr")
    for i, w in enumerate(W.itertuples(index=False), 4):
        wd = W.iloc[i - 4]
        vals = [wd["qid"], wd["doc"], wd["status|G"], wd["status|V"]]
        for c, l in cmc: vals += [wd.get(f"{c}|G"), wd.get(f"{c}|V"), None]
        for j, v in enumerate(vals, 1):
            if v is not None: ws.cell(i, j, clean(v)).font = Font(name=F, size=9)
        for k_, (c, l) in enumerate(cmc):
            gcol = 5 + 3 * k_
            ws.cell(i, gcol + 2, f'=IF(OR({L(gcol)}{i}="",{L(gcol+1)}{i}=""),"",{L(gcol)}{i}-{L(gcol+1)}{i})' if use_formulas else clean((wd.get(f"{c}|G") - wd.get(f"{c}|V")) if pd.notna(wd.get(f"{c}|G")) and pd.notna(wd.get(f"{c}|V")) else None)).number_format = "0.000"
        dcor, dmrr = L(corr_col_G + 2), L(mrr_G + 2)
        ws.cell(i, len(cols) - 2, f'=IF({dcor}{i}="","",IF({dcor}{i}>0,"Graph lebih baik",IF({dcor}{i}<0,"Vector lebih baik","Setara")))' if use_formulas else
                ("Graph lebih baik" if wd["corr|G"] > wd["corr|V"] else "Vector lebih baik" if wd["corr|G"] < wd["corr|V"] else "Setara"))
        ws.cell(i, len(cols) - 1, f'=IF({dmrr}{i}="","",IF({dmrr}{i}>0,"Graph lebih baik",IF({dmrr}{i}<0,"Vector lebih baik","Setara")))' if use_formulas else
                ("Graph lebih baik" if wd["mrr|G"] > wd["mrr|V"] else "Vector lebih baik" if wd["mrr|G"] < wd["mrr|V"] else "Setara"))
        notes = []
        if wd["status|G"] in ABSTAIN_STATUS: notes.append("Graph abstain")
        if wd["status|V"] in ABSTAIN_STATUS: notes.append("Vector abstain")
        if wd.get("provisional|G") == 1 or wd.get("provisional|V") == 1: notes.append("skor provisional")
        if wd.get("latency_outlier|G") == 1 or wd.get("latency_outlier|V") == 1: notes.append("latency outlier")
        ws.cell(i, len(cols), "; ".join(notes)).font = Font(name=F, size=9)
    for j in range(1, len(cols) + 1): ws.column_dimensions[L(j)].width = 14 if j > 4 else 22
    ws.column_dimensions[L(len(cols))].width = 34; ws.freeze_panes = "C4"; ws.auto_filter.ref = f"A3:{L(len(cols))}{3 + n_pairs}"
    rr_ = 3 + n_pairs + 2; title(ws, rr_, "Rekap hasil per pertanyaan")
    for i, lab_ in enumerate(("Graph lebih baik", "Setara", "Vector lebih baik"), rr_ + 1):
        ws.cell(i, 1, lab_); a, b = f"{L(len(cols)-2)}4:{L(len(cols)-2)}{3+n_pairs}", f"{L(len(cols)-1)}4:{L(len(cols)-1)}{3+n_pairs}"
        ws.cell(i, 2, f'=COUNTIF({a},"{lab_}")' if use_formulas else int((((W["corr|G"] > W["corr|V"]) if lab_.startswith("Graph") else (W["corr|G"] < W["corr|V"]) if lab_.startswith("Vector") else (W["corr|G"] == W["corr|V"])).sum())))
        ws.cell(i, 3, f'=COUNTIF({b},"{lab_}")' if use_formulas else int((((W["mrr|G"] > W["mrr|V"]) if lab_.startswith("Graph") else (W["mrr|G"] < W["mrr|V"]) if lab_.startswith("Vector") else (W["mrr|G"] == W["mrr|V"])).sum())))
    ws.cell(rr_, 2, "Correctness").font = Font(name=F, bold=True); ws.cell(rr_, 3, "MRR").font = Font(name=F, bold=True)

    # ---------------- Summary & Findings
    ws = sheet("Summary & Findings", "C0392B"); ws.column_dimensions["A"].width = 34; ws.column_dimensions["B"].width = 140
    title(ws, 1, "Summary & Findings (dihasilkan otomatis dari perhitungan; tidak diedit manual)", 13)
    r = 3
    for a, b in findings:
        body(ws, a, r, bold=True); body(ws, b, r, 2); ws.row_dimensions[r].height = max(30, 15 * (len(b) // 130 + 1)); r += 1
    r += 1; title(ws, r, "Uji statistik berpasangan (selisih = Graph - Vector)"); r += 1
    keep = ["kelompok", "metrik", "n_pasangan", "mean_G", "mean_V", "mean_diff", "median_diff", "ci95_lo", "ci95_hi", "G_lebih_tinggi", "setara", "G_lebih_rendah", "uji", "statistik", "p_value", "p_holm", "catatan"]
    Tt = T.reindex(columns=keep).copy(); Tt["Kesimpulan metrik"] = [verdict(x) for _, x in T.iterrows()]
    hdr(ws, r, list(Tt.columns))
    for i, row in enumerate(Tt.itertuples(index=False), r + 1):
        for j, v in enumerate(row, 1):
            c = ws.cell(i, j, clean(v)); c.font = Font(name=F, size=9)
            if isinstance(v, float): c.number_format = "0.000"
    ws.column_dimensions["B"].width = 44
    r += len(Tt) + 3; title(ws, r, "Data yang dikecualikan"); r += 1
    ex = cases[~cases["valid"]][["qid", "method", "status", "alasan_eksklusi"]]
    if len(ex):
        hdr(ws, r, ["Question ID", "Metode", "Status", "Alasan"]); r += 1
        for row in ex.itertuples(index=False):
            for j, v in enumerate(row, 1): ws.cell(r, j, clean(v))
            r += 1
    else: body(ws, "Tidak ada kasus yang dikecualikan.", r); r += 1
    r += 1; title(ws, r, "Hasil validasi data"); r += 1; hdr(ws, r, ["Pemeriksaan", "Tingkat / jumlah / keterangan"]); r += 1
    for row in issues.itertuples(index=False): body(ws, row.pemeriksaan, r); body(ws, f"{row.tingkat} | {row.jumlah} | {row.keterangan}", r, 2); r += 1
    r += 1; title(ws, r, "Keterbatasan"); r += 1
    for t in LIMITATIONS: body(ws, "-", r); body(ws, t, r, 2); r += 1
    order = ["README", "Summary & Findings", "Golden Set", "Retrieval Metrics", "Generation Metrics", "Comparison Matrix", "Raw Results", "Raw Retrieval", "Raw LLM Context", "Raw Trace", "Manual Review", "Run History", "Run Config"]
    wb._sheets = [wb[n] for n in order if n in wb.sheetnames]
    wb.save(path)
    return path


_UNIVERSE = []


def run_analysis(path, golden_json=None, sheet_map=None, column_map=None, k=K_DEFAULT):
    """Alur lengkap. Mengembalikan dict berisi semua objek analisis."""
    global _UNIVERSE
    data, report = load_input(path, sheet_map, column_map)
    if "golden" not in data:
        if golden_json: data["golden"] = load_golden_json(golden_json)
        else:
            data["golden"] = data["results"].drop_duplicates("qid", keep="last")[["qid", "doc", "question", "ref_answer", "expected_files"]].assign(evidence=np.nan)
    issues, cases = validate(data, k)
    M = compute_case_metrics(data, cases, k)
    if M.empty: raise DataFormatError("Tidak ada kasus valid untuk dianalisis. Lihat tabel validasi untuk alasan eksklusi.")
    W = paired_wide(M); T = paired_tests(W)
    cm_ret, universe = retrieval_confusion(M, data, k); _UNIVERSE = universe
    cms = answer_confusion(M); cms_conf = answer_confusion(M, only_confirmed=True)
    D = per_document(M); A_only = answered_only(M)
    findings = build_findings(M, W, T, cases, issues, k)
    return dict(data=data, report=report, issues=issues, cases=cases, M=M, W=W, T=T, cm_ret=cm_ret, universe=universe, cms=cms, cms_conf=cms_conf, D=D, A_only=A_only, findings=findings, k=k)
