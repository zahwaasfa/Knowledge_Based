"""Create a shareable ARCANA source package without secrets or stale archives."""
from __future__ import annotations

import argparse
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "reports" / "knowledgebased_arcana_matriks_final_20261019.zip"
EXCLUDED_DIRS = {".git", ".matrix_tmp", "__pycache__", ".pytest_cache", ".venv", "venv", "node_modules"}
EXCLUDED_FILES = {
    "contoh_evaluasi_10_pertanyaan_simulasi.xlsx",
    "matriks_penilaian_rag_notetaker_terisi_simulasi.xlsx",
    "rag_evaluation_20261018_224043.json",
}


def include_file(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if any(part in EXCLUDED_DIRS for part in rel.parts[:-1]):
        return False
    name = path.name
    if name.startswith("~$"):
        return False
    if name == ".env" or (name.startswith(".env.") and name != ".env.example"):
        return False
    if name in EXCLUDED_FILES or name.endswith(".inspect.ndjson"):
        return False
    if path.suffix.lower() in {".zip", ".pyc", ".pyo"}:
        return False
    return path.is_file()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    entries = [p for p in ROOT.rglob("*") if p.resolve() != output and include_file(p)]
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=8) as archive:
        for path in sorted(entries):
            rel = path.relative_to(ROOT).as_posix()
            archive.write(path, f"knowledgebased/{rel}")
    with zipfile.ZipFile(output) as archive:
        bad_member = archive.testzip()
        if bad_member:
            raise RuntimeError(f"ZIP gagal diverifikasi pada: {bad_member}")
        names = archive.namelist()
        if any(name.endswith("/.env") or name.endswith("/.env.local") for name in names):
            raise RuntimeError("ZIP memuat berkas environment rahasia")
        required = {
            "knowledgebased/reports/matriks_penilaian_rag_notetaker_integrasi_aktual_20261019.xlsx",
            "knowledgebased/reports/rag_evaluation_20261018_actual.json",
            "knowledgebased/scripts/evaluate_rag.py",
            "knowledgebased/scripts/export_eval_to_matrix_fallback.py",
            "knowledgebased/docs/PAKET_DAN_EVALUASI_MATRIKS.md",
        }
        missing = required.difference(names)
        if missing:
            raise RuntimeError(f"ZIP tidak lengkap; file wajib hilang: {sorted(missing)}")
        if any(name.endswith(".inspect.ndjson") or name.endswith(".zip") for name in names):
            raise RuntimeError("ZIP memuat berkas inspeksi sementara atau ZIP lama")
    print(f"ZIP: {output}")
    print(f"File: {len(entries)}; ukuran: {output.stat().st_size:,} byte; CRC: valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
