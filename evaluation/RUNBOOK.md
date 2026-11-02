# Menjalankan evaluasi Vector RAG vs Graph RAG

## Prasyarat

1. Jalankan perintah dari direktori project di mana `docker-compose.yml` berada.
2. Siapkan `.env` project dengan kredensial Neo4j dan provider LLM yang valid. Jangan membagikan isi `.env`.
3. Pastikan Neo4j yang dikonfigurasi dapat dijangkau dan corpus Notetaker sudah di-ingest, termasuk indeks/embedding Vector RAG. Jangan jalankan loader atau perintah reset sebagai bagian benchmark.
4. Jalankan API ARCANA terlebih dahulu dan cek health secara manual. Dari terminal Windows/PowerShell: `Invoke-RestMethod http://localhost:8001/kb/health`. Dari WSL gunakan `curl http://localhost:8001/kb/health`. Health adalah pemeriksaan kesiapan layanan, bukan bukti kebenaran jawaban.
5. Di perintah Docker di bawah, API diakses internal sebagai `http://kb-api:8000`. Pastikan service `kb-api` hidup (`docker compose up -d kb-api`).

## Run ulang pertanyaan yang sebelumnya NOT_FOUND

Batch pertama berisi lima pertanyaan (10 request: Vector dan Graph untuk tiap pertanyaan):

```bash
docker compose run --rm loader python scripts/evaluate_rag.py --api http://kb-api:8000 --corpus notetaker --golden-set evaluation/golden_set_notetaker_75.json --mode both --ids NT-004-Q01,NT-004-Q06,NT-004-Q11 --delay 40 --append-workbook --replace-existing-ids --workbook-output reports/rag_evaluation_20261024.xlsx
```

Batch kedua berisi empat pertanyaan (8 request):

```bash
docker compose run --rm loader python scripts/evaluate_rag.py --api http://kb-api:8000 --corpus notetaker --golden-set evaluation/golden_set_notetaker_75.json --mode both --ids NT-003-Q06,NT-004-Q07,NT-004-Q08,NT-004-Q09,NT-004-Q10 --delay 40 --append-workbook --replace-existing-ids --workbook-output reports/rag_evaluation_20261024.xlsx
```

Flag `--replace-existing-ids` mengganti baris detail lama untuk ID yang dipilih (untuk Graph dan Vector) dengan hasil terbaru. ID lain tetap ada. Riwayat sesi dan ringkasan metrik per sesi tetap dipertahankan. Path workbook harus sama pada kedua perintah. Tutup workbook di Excel sebelum menjalankan.

Untuk run biasa yang belum pernah ada di workbook, gunakan `--append-workbook --workbook-output reports/nama_workbook.xlsx`; tambahkan `--replace-existing-ids` bila memang ingin mengganti hasil detail ID yang sama. `--replace-existing-ids` otomatis mengaktifkan append workbook. Jangan gunakan `--no-excel` jika ingin output Excel.

## Benchmark penuh

Hapus `--ids ...` dari contoh di atas untuk memakai seluruh golden set. Targetnya 75 pertanyaan × 2 metode = 150 request. `--top-k` default-nya 5. Perintah benchmark tidak dijalankan selama persiapan project ini.

## Output lokal

Secara default setiap run menyimpan file bertimestamp di `reports/` sehingga run sebelumnya tidak tertimpa. Dengan `--append-workbook`, JSON tetap per sesi, sementara workbook diarahkan ke satu path tetap:

- `rag_evaluation_<timestamp>.json`: data mentah lengkap sebagai sumber audit.
- `rag_evaluation_<timestamp>.xlsx`: satu workbook dengan sheet Ringkasan, Matriks Metrik, Permintaan, Retrieval Detail, Konteks LLM, Trace, Log Error, Review Manual, dan Konfigurasi. Metrik retrieval, generasi, dan operasional tercantum; nilai yang membutuhkan peninjauan manusia atau responden dibiarkan kosong.

Workbook tidak membutuhkan file template Excel. Jika preflight API gagal, JSON dan workbook laporan preflight tetap dibuat, dan tidak ada request pertanyaan yang dijalankan. Jika ekspor Excel gagal, JSON mentah tetap tersimpan.

## Perhitungan dan interpretasi

Relevansi retrieval otomatis dicocokkan dengan nama file pada `expected_source_files`: Precision@k menghitung chunk relevan file per chunk dibagi seluruh chunk yang diambil; Recall@k menghitung dokumen relevan unik yang ditemukan dibagi dokumen relevan yang diharapkan; MRR memakai posisi chunk relevan pertama; Hit Rate@k menandai pertanyaan yang memiliki minimal satu chunk relevan. Karena ini pencocokan dokumen, periksa isi chunk di `Retrieval Detail` sebelum menafsirkan sebagai relevansi semantik.

Latency disimpan per request; Availability / Success Rate adalah request API sukses dibagi yang dicoba, terpisah dari status substansi jawaban seperti `NOT_FOUND` atau `LLM_ERROR`. Faithfulness, Answer Correctness, Answer Relevancy, Citation Precision, dan Citation Coverage tidak akan diberi nilai rekaan: tinjau sesuai antrean `Review Manual`. Jawaban acuan, konteks aktual yang dikembalikan API, jawaban dan sitasi dapat ditelusuri di workbook.


## Analisis hasil (Colab) dan perapian workbook

SUS dan metrik audit/traceability TIDAK lagi bagian evaluasi. Untuk merapikan workbook ke struktur baku dan menghitung ulang metrik tanpa menjalankan ulang API: `python scripts/build_clean_workbook.py --input reports/<file>.xlsx --golden evaluation/golden_set_notetaker_75.json --output reports/<file>_RAPI.xlsx`. Untuk analisis statistik berpasangan dan visualisasi, unggah workbook ke notebook `ARCANA_GraphRAG_vs_VectorRAG_Evaluation.ipynb` di Google Colab (logika inti: `evaluation/arcana_eval.py`).
