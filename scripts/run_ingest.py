"""Incremental ingestion Bappenas atau Notetaker ke Neo4j.
Pakai: python -m scripts.run_ingest [--only DOC-001 DOC-002] [--notetaker-only] [--force] [--no-seed]"""
import argparse
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kb.ingest import run  # noqa: E402

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--no-seed", action="store_true")
    ap.add_argument("--notetaker-only", action="store_true", help="Muat Markdown Arcana dengan JSON pasangannya sebagai metadata")
    ap.add_argument("--force", action="store_true", help="Paksa ingest ulang; gunakan --only agar tidak memproses ulang seluruh cakupan")
    a = ap.parse_args()
    r = run(a.only, not a.no_seed, a.notetaker_only, a.force)
    n_chunks = sum(x["chunks"] for x in r["per_document"])
    print(f'Selesai: {r["documents"]} diproses, {len(r["skipped_documents"])} dilewati, {n_chunks} chunk ditulis, {r["crosslinks"]} crosslink, {len(r["errors"])} galat')
    sys.exit(1 if r["errors"] or any(x["status"] != "complete" for x in r["per_document"]) else 0)
