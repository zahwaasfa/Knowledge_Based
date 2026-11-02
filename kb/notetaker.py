"""Bangun metadata dokumen Arcana dari pasangan JSON dan Markdown."""
from __future__ import annotations

import json
import hashlib
import re
from pathlib import Path

from . import metadata
from .config import S


_LEGACY_DOC_IDS = {
    "20260818-13-08-41-pembahasan-masukan-akademisi-untuk-draft-p-2026-08-18": "NT-001",
    "20260904-09-08-09-pengetahuan-tata-kelola-pengetahuan-pemanf-2026-09-04": "NT-002",
    "20260908-13-24-58-sharing-knowledge-pengelolaan-dan-pengemba-2026-09-08": "NT-003",
    "20261008-10-08-37-rapat-lanjutan-pembahasan-pekerjaan-konsul-2026-10-08": "NT-004",
    "koordinasi-teknis-persiapan-serah-terima-hasil-pengembangan--2026-07-15": "NT-005",
}


def _stable_doc_id(path: Path) -> str:
    known_id = _LEGACY_DOC_IDS.get(path.stem)
    if known_id:
        return known_id
    suffix = hashlib.sha256(path.stem.encode("utf-8")).hexdigest()[:10].upper()
    return f"NT-{suffix}"


def _markdown_title(path: Path) -> str:
    first = path.read_text(encoding="utf-8", errors="ignore").splitlines()[0]
    title = re.sub(r"^\s*#\s*", "", first).strip()
    match = re.search(r"\[(.+)]\s*$", title)
    return (match.group(1) if match else title).strip()


def load_notetaker_docs() -> list[dict]:
    """Read Markdown as content and matching Arcana JSON as document metadata."""
    markdown_dir = S.notetaker_markdown_dir
    json_dir = S.notetaker_json_dir
    if not markdown_dir.exists():
        raise FileNotFoundError(f"Folder transkrip tidak ditemukan: {markdown_dir}")

    markdown_paths = sorted(markdown_dir.glob("*.md"))
    markdown_stems = {path.stem for path in markdown_paths}
    for sidecar in sorted(json_dir.glob("*.json")):
        if sidecar.stem not in markdown_stems:
            print(f"[warn] JSON tanpa Markdown pasangan, dilewati: {sidecar.name}")

    docs = []
    for index, path in enumerate(markdown_paths, 1):
        sidecar = json_dir / f"{path.stem}.json"
        raw = json.loads(sidecar.read_text(encoding="utf-8")) if sidecar.exists() else {}
        title = str(raw.get("title") or _markdown_title(path)).strip()
        date = str(raw.get("date") or "")[:10]
        speakers = raw.get("speakerLabels") or {}
        speaker_count = len(set(speakers.values())) if isinstance(speakers, dict) else 0
        segments = raw.get("segments") or []
        details = ["Transkrip Arcana Notetaker"]
        if not sidecar.exists():
            details.append("JSON metadata pasangan tidak ditemukan; judul diambil dari Markdown")
        if date:
            details.append(f"tanggal: {date}")
        if raw.get("source"):
            details.append(f"sumber: {raw['source']}")
        if speaker_count:
            details.append(f"jumlah pembicara: {speaker_count}")
        if segments:
            details.append(f"jumlah segmen transkrip: {len(segments)}")

        doc = metadata.normalise(
            {
                "Judul": title,
                "Nama File": path.name,
                "Jenis Output": "Transkrip Rapat",
                "Jenis Pengetahuan": "Notulensi dan Transkrip",
                "Deskripsi": "; ".join(details),
                "Tanggal Publikasi": date,
                "Tahun Penyusunan": date[:4],
                "Bidang Kategori": "Arcana Notetaker",
                "Klasifikasi": "Internal",
                "Hak Akses Dokumen": "Tidak dicatat",
            },
            index,
        )
        doc["doc_id"] = _stable_doc_id(path)
        doc["domain"] = "notetaker"
        doc["corpus"] = "notetaker"
        if raw:
            doc["extra"] = {
                "arcana_source": raw.get("source"),
                "arcana_started_at_ms": raw.get("startedAt"),
                "arcana_ended_at_ms": raw.get("endedAt"),
                "arcana_speaker_count": speaker_count,
                "arcana_segment_count": len(segments),
            }
        docs.append(doc)
    return docs
