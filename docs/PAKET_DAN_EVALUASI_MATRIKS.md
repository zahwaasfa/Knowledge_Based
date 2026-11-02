# Paket ARCANA dan pengujian matriks Notetaker

## 1. Ekstrak dan siapkan konfigurasi

Ekstrak ZIP ke folder proyek, buka terminal pada folder yang berisi docker-compose.yml, lalu salin .env.example menjadi .env. Atur nilai berikut menggunakan kredensial pribadi Anda:

    NEO4J_URI=neo4j+s://<id-instance-anda>.databases.neo4j.io
    NEO4J_URI_DOCKER=neo4j+s://<id-instance-anda>.databases.neo4j.io
    NEO4J_USERNAME=<username-aura>
    NEO4J_PASSWORD=<password-aura>
    EMBEDDINGS=true
    USE_LLM=true
    GROQ_API_KEY=<api-key-groq>

Jangan membagikan .env. NEO4J_URI_DOCKER diatur juga karena Compose memakai nilai itu untuk container aplikasi. Untuk Aura, jangan nyalakan service Neo4j lokal dengan profile local-db.

## 2. Bangun dan jalankan aplikasi

Dengan Docker Desktop aktif:

    docker compose up -d --build kb-api streamlit-ui
    docker compose ps
    curl -i --max-time 10 http://localhost:8001/kb/health

Lanjutkan setelah health API mengembalikan HTTP 200 dan "neo4j":"connected". Halaman UI ada di http://localhost:8501.

## 3. Pastikan data Notetaker ada di Aura

Jika ingin menyelaraskan sumber Notetaker dalam ZIP ke Aura, jalankan:

    docker compose run --rm loader python -m scripts.run_ingest --notetaker-only --no-seed

Loader incremental melewati dokumen yang fingerprint-nya sama dan lengkap. Periksa reports/ingest_report.md. Jangan gunakan --force kecuali memang ingin membangun ulang dokumen yang dipilih.

## 4. Jalankan evaluasi Graph RAG dan Vector RAG

Jalankan dari folder proyek:

    docker compose exec kb-api python scripts/evaluate_rag.py --api http://localhost:8000 --corpus notetaker --golden-set evaluation/golden_set_notetaker_75.json --mode both --top-k 5

Skrip menguji 75 pertanyaan pada kedua metode (150 request), menyimpan JSON mentah, lalu membuat salinan workbook baru di reports/. Workbook sumber tidak ditimpa. Keberhasilan eksekusi bukan bukti bahwa semua jawaban benar; cek ringkasan jumlah request selesai/gagal dan kelas kegagalan.

pwd
ls -l scripts/evaluate_rag.py evaluation/golden_set_notetaker_75.json
docker compose exec kb-api pwd
docker compose exec kb-api ls -l /app/scripts/evaluate_rag.py
/mnt/c/Users/asfa_/knowledgebased2

docker compose exec kb-api python scripts/evaluate_rag.py --api http://localhost:8000 --corpus notetaker --golden-set evaluation/golden_set_notetaker_75.json --mode both --top-k 5 --output reports/rag_evaluation_rerun.json --workbook reports/matriks_penilaian_rag_notetaker_integrasi.xlsx --workbook-output reports/matriks_penilaian_rag_notetaker_integrasi_aktual_rerun.xlsx 
echo $?

docker compose exec kb-api python scripts/evaluate_rag.py \
  --api http://127.0.0.1:8000 \
  --corpus notetaker \
  --golden-set evaluation/golden_set_notetaker_75.json \
  --mode both \
  --top-k 5 \
  --output reports/rag_evaluation_21_1033.json \
  --workbook reports/matriks_penilaian_rag_notetaker_integrasi.xlsx \
  --workbook-output reports/matriks_penilaian_rag_notetaker_integrasi_aktual_21_1033.xlsx

docker compose run --rm loader python scripts/evaluate_rag.py \
  --corpus notetaker \
  --golden-set evaluation/golden_set_notetaker_75.json \
  --mode both \
  --ids NT-005-Q06,NT-005-Q07,NT-005-Q08,NT-005-Q09,NT-005-Q10 \
  --delay 40 \
  --output reports/rag_evaluation_NT005_3.json \
  --workbook reports/matriks_penilaian_rag_notetaker_integrasi.xlsx \
  --workbook-output reports/matriks_penilaian_rag_notetaker_NT005_3.xlsx



## 4.1 ganti api 
docker compose up -d --force-recreate kb-api


  

## 5. Selesaikan penilaian manual di Excel

1. Buka workbook matriks_penilaian_rag_notetaker_integrasi_aktual_*.xlsx yang paling baru.
2. Di Retrieval Detail, untuk setiap kandidat dengan status tercatat Ya pada kolom L, baca kutipan kolom K dan tandai kolom J Ya hanya jika chunk benar-benar membantu menjawab pertanyaan; selain itu tandai Tidak. Kolom H hanya mencocokkan nama file expected, bukan menilai relevansi semantik.
3. Di Evaluasi Jawaban, isi jumlah klaim faktual (K), klaim yang bersitasi dan didukung (L), Faithfulness (R), Correctness (S), alasan juri (T), dan Citation Precision (U). Validitas struktural sitasi di kolom M tidak membuktikan dukungan semantik.
4. Periksa konteks aktual, jawaban sistem, source ID, dan status run. Untuk klaim yang disitasi, bandingkan klaim dengan kutipan chunk yang ditampilkan pada Retrieval Detail dan konteks yang dicatat.
5. Buka Ringkasan setelah Excel menghitung ulang formula. Precision@5, Recall@5, MRR, Hit Rate, serta Citation Coverage hanya dapat ditafsirkan setelah penilaian manual terkait diisi.
6. Simpan hasil penilaian sebagai salinan baru agar hasil API mentah tetap tersedia untuk audit.

## Hasil run yang disertakan

Paket ini menyertakan run aktual 75 pertanyaan × 2 metode bertanggal 19 Oktober 2026. Seluruh 150 request selesai; dua output NT-003-Q11 dan NT-003-Q12 ditandai Output LLM gagal validasi karena payload jawabannya mengandung karakter kontrol. JSON mentah mempertahankan payload asli, sedangkan salinan Excel membersihkan karakter yang tidak dapat disimpan di format workbook. Penilaian relevansi chunk dan kualitas semantik tetap memerlukan reviewer.
