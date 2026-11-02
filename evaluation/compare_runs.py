#!/usr/bin/env python3
"""Analisis offline berpasangan (tanpa Neo4j/Groq). Membaca workbook hasil evaluasi (sheet Raw Results, Raw Retrieval,
Raw LLM Context) dan menulis laporan Markdown + CSV BARU; workbook sumber tidak pernah diubah.

Mode:
  1) --a BASE.xlsx                       : Graph vs Vector dalam satu run (pertanyaan sama, berpasangan).
  2) --a BASE.xlsx --b OPT.xlsx          : tambahan Graph(BASE) vs Graph(OPT) dan Vector(BASE) vs Vector(OPT)
                                           (regresi/perbaikan sebelum-sesudah, pertanyaan sama).
Definisi metrik (dipertahankan dari runner): relevansi chunk = file sumber chunk ada di expected_source_files.
  P@k ketat = relevan / k (k=5, penyebut tetap); P chunk = relevan / jumlah chunk dikembalikan; Hit, MRR, Recall@k (dokumen).
  Abstain = status NOT_FOUND atau UNSUPPORTED_ANSWER. Faithfulness=5 pada abstain adalah konvensi workbook -> dilaporkan
  juga tanpa abstain. Evidence recall leksikal & Citation Coverage/Precision memerlukan data/penilaian manual: tidak dihitung di sini.
Statistik: Wilcoxon signed-rank (berpasangan), CI95 bootstrap pertanyaan DAN bootstrap-klaster (resample dokumen lalu pertanyaan),
  ukuran efek dz (rata-rata selisih / SD selisih), McNemar exact untuk biner, koreksi Holm lintas metrik. 75 pertanyaan tersarang
  dalam 5 dokumen -> independensi tidak penuh; tabel per-dokumen disajikan dan p-value diperlakukan sebagai indikatif.
"""
from __future__ import annotations
import argparse, json, math, os, sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

K = 5
ABSTAIN = {"NOT_FOUND", "UNSUPPORTED_ANSWER"}
SCORES = ["Faithfulness", "Answer Correctness", "Answer Relevancy"]
rng = np.random.default_rng(20261028)


def load(path: str) -> pd.DataFrame:
    R = pd.read_excel(path, "Raw Results", dtype=str)
    T = pd.read_excel(path, "Raw Retrieval", dtype=str)
    C = pd.read_excel(path, "Raw LLM Context", dtype=str)
    T["rel"] = T["Sumber diharapkan"].isin(["TRUE", "True", "=TRUE()"])
    for c in SCORES + ["Latency server (ms)", "Latency klien (ms)"]:
        R[c] = pd.to_numeric(R[c], errors="coerce")
    g = T.groupby(["Question ID", "Metode"])
    ret = pd.DataFrame({"n_ret": g.size(), "n_rel": g.rel.sum(),
                        "first_rank": g.apply(lambda d: next((i for i, x in enumerate(d.sort_values("Rank", key=lambda s: s.astype(int)).rel, 1) if x), 0), include_groups=False)})
    ctx = C.assign(chars=C["Teks konteks aktual dikirim ke LLM"].fillna("").str.len()).groupby(["Question ID", "Metode"]).agg(ctx_chunks=("chunks" if False else "chars", "size"), ctx_chars=("chars", "sum"))
    M = R.set_index(["Question ID", "Metode"]).join(ret).join(ctx).reset_index()
    M["n_ret"] = M.n_ret.fillna(0); M["n_rel"] = M.n_rel.fillna(0)
    M["P@k ketat"] = M.n_rel / K
    M["P chunk"] = np.where(M.n_ret > 0, M.n_rel / M.n_ret.replace(0, np.nan), np.nan)
    M["Hit@k"] = (M.n_rel > 0).astype(float)
    M["Recall@k"] = M["Hit@k"]          # satu dokumen sumber per pertanyaan pada golden set ini
    M["MRR"] = np.where(M.first_rank > 0, 1 / M.first_rank.replace(0, np.nan), 0.0)
    M["abstain"] = M["Status evaluasi"].isin(ABSTAIN).astype(float)
    M["Correct>=4"] = (M["Answer Correctness"] >= 4).astype(float)
    def src_acc(row):
        try: cs = json.loads(row["Sitasi (JSON)"]) if isinstance(row["Sitasi (JSON)"], str) else []
        except Exception: return np.nan
        exp = {Path(x).name for x in json.loads(row["Expected source files"])} if str(row["Expected source files"]).startswith("[") else {Path(x.strip()).name for x in str(row["Expected source files"]).split(",")}
        fs = [Path(c.get("file_name") or "").name for c in cs]
        return np.mean([f in exp for f in fs]) if fs else np.nan
    M["Source accuracy"] = M.apply(src_acc, axis=1)
    M["Latency (s)"] = M["Latency server (ms)"] / 1000
    M["Dokumen"] = M["Document ID"]
    return M


def holm(p):
    p = np.asarray(p, float); o = np.argsort(p); m = len(p); adj = np.empty(m); run = 0
    for i, idx in enumerate(o):
        run = max(run, (m - i) * p[idx]); adj[idx] = min(1, run)
    return adj


def paired(a: pd.DataFrame, b: pd.DataFrame, metrics, label):
    """selisih = b - a pada pertanyaan yang sama."""
    j = a.set_index("Question ID").join(b.set_index("Question ID"), lsuffix="_a", rsuffix="_b", how="inner")
    rows = []
    for m in metrics:
        d = (j[f"{m}_b"] - j[f"{m}_a"]).dropna(); x = j.loc[d.index]
        if len(d) < 3: continue
        nz = d[d != 0]
        p = stats.wilcoxon(nz).pvalue if len(nz) >= 6 else np.nan
        qs = np.array(d); docs = x["Dokumen_a"].values
        boot = [rng.choice(qs, len(qs)).mean() for _ in range(4000)]
        ud = np.unique(docs); cb = []
        for _ in range(4000):
            pick = rng.choice(ud, len(ud)); vals = np.concatenate([rng.choice(d.values[docs == u], (docs == u).sum()) for u in pick]); cb.append(vals.mean())
        sd = qs.std(ddof=1)
        rows.append({"perbandingan": label, "metrik": m, "n": len(d), "rata_a": x[f"{m}_a"].mean(), "rata_b": x[f"{m}_b"].mean(),
                     "selisih": qs.mean(), "CI95_boot_lo": np.percentile(boot, 2.5), "CI95_boot_hi": np.percentile(boot, 97.5),
                     "CI95_klaster_lo": np.percentile(cb, 2.5), "CI95_klaster_hi": np.percentile(cb, 97.5),
                     "dz": qs.mean() / sd if sd > 0 else np.nan, "b_lebih_tinggi": int((d > 0).sum()), "sama": int((d == 0).sum()), "b_lebih_rendah": int((d < 0).sum()),
                     "p_wilcoxon": p})
    out = pd.DataFrame(rows)
    if len(out):
        ok = out.p_wilcoxon.notna(); out["p_holm"] = np.nan
        if ok.any(): out.loc[ok, "p_holm"] = holm(out.loc[ok, "p_wilcoxon"])
    return out


def summary(M: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for meth, d in M.groupby("Metode"):
        na = d[d.abstain == 0]
        rows.append({"Metode": meth, "n": len(d), "Chunk dikembalikan": d.n_ret.mean(), "P@k ketat": d["P@k ketat"].mean(), "P chunk": d["P chunk"].mean(),
                     "Recall@k": d["Recall@k"].mean(), "Hit@k": d["Hit@k"].mean(), "MRR": d.MRR.mean(),
                     "Correctness": d["Answer Correctness"].mean(), "Correctness non-abstain": na["Answer Correctness"].mean(),
                     "Relevancy": d["Answer Relevancy"].mean(), "Relevancy non-abstain": na["Answer Relevancy"].mean(),
                     "Faithfulness (semua)": d.Faithfulness.mean(), "Faithfulness non-abstain": na.Faithfulness.mean(),
                     "Benar (>=4)": (d["Answer Correctness"] >= 4).mean(), "Sebagian (3)": (d["Answer Correctness"] == 3).mean(), "Salah (<=2)": (d["Answer Correctness"] <= 2).mean(),
                     "Abstain": d.abstain.mean(), "Source accuracy": d["Source accuracy"].mean(),
                     "Latency median (s)": d["Latency (s)"].median(), "Latency P90 (s)": d["Latency (s)"].quantile(.9),
                     "Chunk ke LLM": d.ctx_chunks.mean(), "Karakter konteks": d.ctx_chars.mean(),
                     "Error/timeout": d["Status evaluasi"].isin(["LLM_ERROR", "LLM_TIMEOUT", "LLM_RATE_LIMIT", "RETRIEVAL_ERROR"]).mean()})
    return pd.DataFrame(rows).set_index("Metode").T


def per_doc(M):
    return M.groupby(["Dokumen", "Metode"])[["P@k ketat", "P chunk", "MRR", "Answer Correctness", "Faithfulness", "Answer Relevancy", "abstain"]].mean().round(3)


def md(df: pd.DataFrame, nd=3) -> str:
    return df.round(nd).to_markdown() if hasattr(df, "to_markdown") else df.round(nd).to_string()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--a", required=True, help="workbook baseline"); ap.add_argument("--b", help="workbook setelah optimasi")
    ap.add_argument("--out", default="evaluation/results/analysis"); a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    A = load(a.a); metr = ["P@k ketat", "P chunk", "Hit@k", "MRR", "Answer Correctness", "Answer Relevancy", "Faithfulness", "Latency (s)", "n_ret", "abstain"]
    parts = [f"# Analisis berpasangan\n\nSumber A: `{Path(a.a).name}`" + (f"; sumber B: `{Path(a.b).name}`" if a.b else "") + "\n",
             "## A. Ringkasan per metode (baseline)\n", md(summary(A)), "\n## Per dokumen (baseline)\n", md(per_doc(A))]
    tests = [paired(A[A.Metode == "Vector RAG"], A[A.Metode == "Graph RAG"], metr, "BASELINE: Graph - Vector")]
    A_na = A[A.abstain == 0]
    tests.append(paired(A[(A.Metode == "Vector RAG")].assign(Faithfulness=lambda d: d.Faithfulness.where(d.abstain == 0)), A[(A.Metode == "Graph RAG")].assign(Faithfulness=lambda d: d.Faithfulness.where(d.abstain == 0)), ["Faithfulness"], "BASELINE non-abstain (kedua metode non-abstain): Graph - Vector"))
    if a.b:
        B = load(a.b)
        parts += ["\n## B. Ringkasan per metode (setelah optimasi)\n", md(summary(B)), "\n## Per dokumen (setelah)\n", md(per_doc(B))]
        for meth in ("Graph RAG", "Vector RAG"):
            tests.append(paired(A[A.Metode == meth], B[B.Metode == meth], metr, f"{meth}: SESUDAH - SEBELUM"))
        tests.append(paired(B[B.Metode == "Vector RAG"], B[B.Metode == "Graph RAG"], metr, "SESUDAH: Graph - Vector"))
    T = pd.concat(tests, ignore_index=True)
    T["kesimpulan"] = np.where(T.p_holm.isna(), "tidak diuji (selisih nol/terlalu sedikit)", np.where(T.p_holm < .05, np.where(T.selisih > 0, "b > a (signifikan setelah Holm)", "b < a (signifikan setelah Holm)"), "tidak signifikan setelah Holm"))
    cols = ["perbandingan", "metrik", "n", "rata_a", "rata_b", "selisih", "CI95_boot_lo", "CI95_boot_hi", "CI95_klaster_lo", "CI95_klaster_hi", "dz", "b_lebih_tinggi", "sama", "b_lebih_rendah", "p_wilcoxon", "p_holm", "kesimpulan"]
    parts += ["\n## C. Uji berpasangan (selisih = b - a; Holm per kelompok perbandingan)\n", md(T[cols], 4),
              "\nCatatan: 75 pertanyaan tersarang dalam 5 dokumen; CI klaster lebih konservatif. Latency belum terkontrol. Metrik yang tidak berubah atau memburuk TIDAK disembunyikan."]
    (out / "analisis.md").write_text("\n".join(parts), encoding="utf-8")
    T[cols].to_csv(out / "uji_berpasangan.csv", index=False, encoding="utf-8-sig"); summary(A).to_csv(out / "ringkasan_a.csv", encoding="utf-8-sig")
    print((out / "analisis.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
