"""Rapikan workbook hasil pengujian ke struktur baku dan hitung ulang metrik. Tidak memanggil API/Neo4j/Groq.
Contoh:
  python scripts/build_clean_workbook.py --input reports/rag_evaluation_20261024_hasil_review_LENGKAP.xlsx \
      --golden evaluation/golden_set_notetaker_75.json --output reports/rag_evaluation_RAPI.xlsx
File input tidak pernah ditimpa."""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "evaluation"))
import pandas as pd
import arcana_eval as ae


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--input", required=True); p.add_argument("--output", required=True)
    p.add_argument("--golden", default=None, help="golden_set_*.json (opsional; dipakai bila workbook tidak punya sheet Golden Set)")
    p.add_argument("--k", type=int, default=ae.K_DEFAULT); p.add_argument("--values-only", action="store_true", help="tulis nilai, bukan rumus")
    a = p.parse_args()
    if Path(a.input).resolve() == Path(a.output).resolve(): raise SystemExit("Output tidak boleh sama dengan input (file asli tidak ditimpa).")
    try: R = ae.run_analysis(a.input, a.golden, k=a.k)
    except ae.DataFormatError as e: raise SystemExit(f"KESALAHAN FORMAT: {e}")
    ae.build_workbook(a.output, R["data"], R["M"], R["W"], R["T"], R["cases"], R["issues"], R["D"], R["cm_ret"], R["cms"], R["cms_conf"],
                      R["A_only"], R["findings"], R["data"]["golden"], k=a.k, use_formulas=not a.values_only, source_name=Path(a.input).name)
    print(f"OK: {a.output} | kasus valid={len(R['M'])} | pasangan={len(R['W'])}")


if __name__ == "__main__":
    main()
