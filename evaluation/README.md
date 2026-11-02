# Rencana evaluasi knowledge base

**Petunjuk benchmark yang berlaku untuk runner baru:** [`RUNBOOK.md`](RUNBOOK.md). Jalankan `python evaluation/run_full_evaluation.py` dari root proyek setelah prasyarat dipenuhi. Skrip lama `scripts/evaluate_rag.py` disimpan untuk kompatibilitas historis; jangan gunakan sebagai perintah benchmark utama.

# Rencana evaluasi knowledge base

Rancangan knowledge graph yang sudah ada tetap dipertahankan. Evaluasi ini membandingkan dua cara mengambil konteks untuk pertanyaan yang sama:

1. **Graph RAG**: jalankan pencarian dan pengambilan konteks melalui API knowledge graph yang sudah ada.
2. **Vector RAG**: gunakan top-k tetangga terdekat dari indeks vektor saja. Mode ini tidak menjalankan full-text, seed QA, ekspansi relasi, entitas, atau query graph untuk mengambil konteks.

Untuk perbandingan yang adil, bekukan snapshot data, model embedding, chunker, nilai k, prompt, model generatif, dan parameter sampling. Jalankan setiap pertanyaan dengan kedua mode pada API/UI yang sama. API mencatat query, jawaban, ID chunk dan sumber, sitasi, confidence, dan latency di `reports/query_runs.jsonl` serta Neo4j sebagai node `:QueryRun`. `confidence_score` adalah penilaian mandiri LLM tentang dukungan bukti, bukan probabilitas terkalibrasi; simpan juga `confidence_method`.

## Metrik retrieval

- **Kesesuaian pertanyaan dan konteks / Precision@k**: chunk relevan dibagi seluruh chunk terambil. Relevansi dinilai dengan sumber yang ditetapkan di golden set; untuk pertanyaan yang butuh beberapa sumber, beri daftar seluruh sumber yang diperlukan.
- **Recall@k**: jumlah sumber yang diperlukan dan ditemukan dibagi jumlah sumber yang diperlukan. Hitung sumber unik.
- **MRR**: rata-rata `1 / peringkat chunk relevan pertama`; nilainya nol jika tidak ada chunk relevan.
- **Hit Rate@k**: proporsi pertanyaan dengan minimal satu chunk relevan pada top-k.
- Laporkan metrik per pertanyaan dan rata-rata; gunakan k yang sama. Untuk ribuan chunk, rekam juga rank chunk relevan dan ukuran korpus, jangan hanya menilai cuplikan yang ditampilkan.

## Metrik jawaban dan sitasi

- **Correctness / Answer Accuracy**: LLM-as-judge skala 1–5 terhadap jawaban emas, disertai audit manual sampel. Jangan anggap skor ini sebagai fakta tanpa pemeriksaan.
- **Faithfulness / grounding**: skala 1–5 untuk dukungan setiap klaim oleh konteks yang benar-benar diterima model. Nilai terpisah dari correctness.
- **Confidence**: catat `confidence_score` (0–1) dan label benar/tidak dari reviewer. Skor adalah penilaian mandiri LLM atas dukungan bukti dan belum terkalibrasi; validasi kalibrasi sebelum menafsirkan Brier score atau kelompok reliabilitas.
- **Citation precision**: sitasi yang benar-benar mendukung klaim dibagi semua sitasi yang diberikan. **Evidence linking**: setiap sitasi harus memuat ID sumber/chunk serta rentang atau kutipan bukti. Tandai kecocokan `exact` bila kutipan sama persis dengan sumber, `partial` bila span lebih panjang tetapi memuat kutipan, dan `unsupported` bila bukti tidak ditemukan. Laporkan proporsi ketiganya.

Judge menerima pertanyaan, konteks retrieval, jawaban emas, jawaban model, sitasi, dan confidence. Nilai faithfulness serta correctness terpisah; jangan beri judge kunci API atau instruksi lain yang tidak relevan. Soal yang tidak bisa dinilai dicatat sebagai `null` beserta alasan, bukan diberi nilai nol.

## Dataset yang disertakan

- Dokumen asli mentor ada di `evaluation/reference/`. Contoh golden set mentor mengacu ke dokumen PDF Bappenas yang tidak ada di paket ini, jadi jangan gabungkan jawabannya dengan skor corpus notetaker.
- `data/notetaker/markdown/`: lima transkrip `.md`, digunakan sebagai berkas sumber untuk ingest dan chunking.
- `data/notetaker/json/`: lima ekspor `.json`. Mode `--notetaker-only` mencocokkan JSON dengan Markdown lewat basename dan memakai judul, tanggal, sumber, jumlah pembicara, serta jumlah segmen sebagai metadata. Isi yang di-chunk tetap Markdown agar tidak menggandakan teks transkrip.
- Lima transkrip Markdown sekarang memiliki pasangan JSON dengan basename yang sama. JSON 8 Oktober yang benar menggantikan JSON 11 September yang sebelumnya tidak memiliki Markdown pasangan.
- `data/bappenas/documents/` disiapkan bagi dokumen sumber Bappenas, tetapi PDF/DOCX dokumen Bappenas tidak ada pada ZIP rancangan yang diterima. `data/bappenas/metadata_bappenas.json` dan `data/bappenas/seed_qa.json` adalah metadata/kumpulan QA, bukan dokumen sumber. Salin dokumen Bappenas ke folder tersebut sebelum menguji golden set lama.
- `golden_set_notetaker_75.json` berisi 15 pertanyaan per lima transkrip (75 total), dengan bukti kutipan yang diverifikasi terhadap berkas sumber dan penanda interval timestamp. Interval tersebut adalah cakupan sampling, bukan pemetaan ke halaman asli.
- `golden_set_notetaker.json` tetap disimpan sebagai set awal yang lebih kecil untuk kompatibilitas; gunakan set 75 pertanyaan untuk benchmark utama.

## Menjalankan data

Setelah API aktif dan corpus `notetaker` selesai di-ingest, jalankan evaluasi yang sama untuk kedua mode. Perintah ini menyimpan hasil mentah dan mengekspor salinan matriks Excel:

```powershell
python scripts/evaluate_rag.py --api http://localhost:8001 --corpus notetaker --golden-set evaluation/golden_set_notetaker_75.json --mode both --top-k 5
```

Setiap eksekusi membuat `reports/rag_evaluation_<timestamp>.json` dan satu workbook multi-sheet `reports/rag_evaluation_<timestamp>.xlsx`. Workbook dibuat mandiri, tanpa workbook sumber/template. Gunakan `--append-workbook --workbook-output reports/nama_workbook_tetap.xlsx` untuk memakai workbook yang sama. Tambahkan `--replace-existing-ids` jika hasil ID yang dipilih harus menggantikan baris detail sebelumnya; ringkasan sesi lama tetap tercatat pada `Riwayat Run`. Jawaban, konteks debug yang benar-benar dikirim ke LLM, sitasi, kandidat Top-5, skor asli API, run ID, dan latensi request direkam terpisah untuk tiap ID dan metode. Jika satu request gagal, yang lain tetap berjalan dan kegagalan dicatat. Jika pemeriksaan awal API gagal, skrip menyimpan laporan preflight JSON dan workbook tanpa menjalankan request pertanyaan.

Relevansi semantik kandidat (`Retrieval Detail` kolom J), jumlah klaim, klaim yang didukung, faithfulness, correctness, alasan juri, dan Citation Precision harus dinilai manual; skrip tidak mengarang skor itu. Workbook menghitung Precision/Recall/MRR/Hit Rate sebagai proxy pencocokan file dari `expected_source_files`; relevansi semantik chunk tetap perlu ditinjau manual. Citation Coverage dihitung dari klaim yang telah ditandai reviewer dan tetap kosong saat belum dinilai. Kecocokan nama file otomatis adalah proxy, bukan bukti bahwa chunk mendukung jawaban.

Ekspor Excel menggunakan `openpyxl` yang tersedia pada image Docker project. Workbook dibuat otomatis tanpa template. Gunakan `--no-excel` hanya jika memang ingin menonaktifkan ekspor workbook.

Pakai mode notetaker agar loader tidak meminta katalog metadata Bappenas dan memuat lima Markdown bersama JSON pasangannya. Isi Markdown menjadi teks sumber yang di-chunk; JSON yang cocok berdasarkan basename memasok metadata (judul, tanggal, sumber, pembicara, dan segmen), bukan duplikat teks transkrip. Gunakan `--no-seed` agar seed QA lama tidak mencemari corpus uji.

Contoh:

```powershell
python -m scripts.run_schema
python -m scripts.run_ingest --notetaker-only --no-seed --force
```

Dengan Docker dan Aura, Graph RAG menggunakan corpus `notetaker` setelah ingest selesai. Untuk Vector RAG, pastikan `.env` proyek aktif berisi `EMBEDDINGS=true`, lalu terapkan indeks dan buat embedding untuk kelima transkrip:

```bash
docker compose run --rm loader python -m scripts.run_schema
docker compose run --rm loader python -m scripts.run_ingest --notetaker-only --no-seed --force
curl -s http://localhost:8001/kb/health
```

Health harus menunjukkan `vector_rag.configured: true`, `vector_rag.index_online: true`, dan `vector_rag.embedded_chunks` lebih dari nol. UI menyediakan pilihan Graph RAG / Vector RAG. API menerima `{"question":"...","top_k":5,"corpus":"notetaker","mode":"vector"}` atau `mode: "graph"`. Jalankan pertanyaan dan top-k yang sama pada kedua mode.

Contoh body API Graph RAG: `{"question":"Apa rencana yang dibahas dalam kunjungan studi ke UGM?","top_k":5,"corpus":"notetaker","mode":"graph"}`. Ganti mode menjadi `vector` untuk baseline vektor. Gunakan golden set untuk menilai jawaban, grounding, sitasi, confidence, dan latency.

Rekam top-k dan jawaban dari masing-masing retrieval sebagai artefak run sebelum menghitung metrik. Perbandingan dianggap mendukung knowledge graph hanya jika peningkatan berulang pada metrik yang ditetapkan dan kualitas sitasi, dengan biaya/latency turut dilaporkan; satu run atau satu nilai agregat tidak cukup untuk klaim umum.
# Ekspor Matriks dari Evaluasi Aktual

Skrip `scripts/evaluate_rag.py` mengekspor workbook multi-sheet memakai `scripts/export_eval_workbook.py` setelah request API selesai (termasuk laporan preflight gagal). Contoh:

```powershell
python scripts/evaluate_rag.py --api http://localhost:8001 --corpus notetaker --golden-set evaluation/golden_set_notetaker_75.json --mode both --top-k 5
```

Hasil JSON mentah dan workbook multi-sheet bertanggal dibuat di `reports/`; workbook sumber tidak diperlukan. Kandidat Top-5 dan latensi diambil dari eksekusi API; relevansi chunk, jumlah klaim, dukungan klaim, Faithfulness, Correctness, dan Citation Precision tetap perlu penilaian manual. Karakter kontrol pada jawaban API ditandai sebagai kegagalan validasi output pada workbook; JSON mentah mempertahankan payload asli.
