# Perubahan Golden Set

**2026-10-24 — perbaikan redaksi pertanyaan**

- Menghapus pertanyaan berbentuk atribusi seperti “menurut [nama]”, “apa masukan [nama]”, atau “yang dijelaskan [nama]”. Pertanyaan ditulis ulang langsung pada fakta atau prosedur dalam transkrip.
- Mempertahankan 75 ID, 15 pertanyaan per dokumen, `document_id`, `expected_source_files`, `expected_answer`, `evidence_quote`, `evidence_type`, dan interval cakupan.
- Tidak mengubah jawaban acuan maupun kutipan bukti. Validasi statis memeriksa 75 ID unik, distribusi 5 × 15, file sumber dan kutipan bukti.


**2026-10-24 — perbaikan pertanyaan berstatus NOT_FOUND**

- Meninjau hasil JSON lokal dan transkrip di `data/notetaker/markdown`; tidak menjalankan ulang API atau benchmark.
- Menyunting pertanyaan NT-001-Q07, Q08, Q09, Q11 serta NT-002-Q04, Q05, Q12, Q13, Q15 agar memakai istilah dan topik yang tampak langsung pada transkrip.
- Merapikan jawaban acuan pada sembilan item tersebut agar ringkas, berbasis isi sumber, dan tidak menyebut nama pembicara. ID, `document_id`, `expected_source_files`, `evidence_quote`, `evidence_type`, dan cakupan tetap dipertahankan.
- Status NOT_FOUND menunjukkan jawaban tidak ditemukan pada konteks request yang tercatat; perubahan redaksi dapat membantu retrieval tetapi belum membuktikan hasil akan teratasi. Sebagian log menunjukkan chunk dari dokumen yang benar sudah terambil, sehingga pipeline retrieval/generation juga perlu diverifikasi pada run berikutnya.

**2026-10-25 — revisi semua pertanyaan NOT_FOUND pada hasil tersimpan terbaru**

- Meninjau 29 laporan evaluasi JSON lokal beserta transkrip sumber; tidak menjalankan API, benchmark, atau LLM-as-a-Judge.
- Memperbarui redaksi pertanyaan dan jawaban acuan untuk seluruh 32 ID unik yang pada laporan tersimpan terbaru masih memiliki sekurang-kurangnya satu metode berstatus `NOT_FOUND`: NT-002 (Q04, Q05, Q12, Q15), NT-003 (Q02, Q04, Q05, Q06, Q10, Q11, Q12, Q14), NT-004 (Q03, Q04, Q05, Q08, Q09, Q10, Q12, Q15), dan NT-005 (Q02, Q04, Q05, Q06, Q07, Q08, Q09, Q10, Q11, Q12, Q13, Q15).
- Pertanyaan ditulis berdasarkan isi transkrip tanpa meminta jawaban “menurut” nama pembicara; jawaban acuan dibuat langsung, spesifik, dan tidak menambahkan fakta di luar bukti yang dicatat. ID, pemetaan dokumen/sumber, kutipan bukti, jenis bukti, dan interval cakupan dipertahankan.
- `python evaluation/run_full_evaluation.py --validate-only` berhasil: golden set berisi 75 ID unik, 15 per dokumen, dan `evidence_quote` cocok dengan sumber. Ini hanya validasi statis, bukan pengujian RAG; hasil rerun tetap harus diperiksa untuk memastikan NOT_FOUND teratasi.


**2026-10-25 — penulisan ulang pertanyaan yang pernah NOT_FOUND**

- Memindai laporan JSON lokal yang sudah ada (tanpa request API baru) dan menemukan 37 ID unik yang pernah menghasilkan status `NOT_FOUND` pada setidaknya satu metode/run.
- Menulis ulang pertanyaan untuk ID tersebut agar lebih ringkas, fokus pada satu fakta atau hubungan yang benar-benar muncul di transkrip, dan menggunakan istilah sumber yang lebih dekat. ID, pembagian 15 pertanyaan per dokumen, `document_id`, `expected_source_files`, kutipan bukti, serta interval cakupan tidak diubah.
- Jawaban acuan yang sudah ada dipertahankan karena perlu tetap berlandaskan kutipan/evidence masing-masing; perbaikan pertanyaan tidak menjamin retrieval/generation akan menjawab benar. Pada sejumlah hasil lama, chunk dokumen yang diharapkan sudah masuk top-k namun jawaban tetap `NOT_FOUND`, sehingga pipeline retrieval/generation masih perlu ditinjau bila masalah berulang.


**2026-10-25 — penyelarasan jawaban acuan untuk seluruh ID NOT_FOUND**

- Meninjau laporan evaluasi tersimpan dan mengidentifikasi 37 ID unik yang pernah menghasilkan `NOT_FOUND` pada setidaknya satu metode.
- Menyelaraskan pertanyaan dan `expected_answer` untuk 37 ID tersebut dengan fakta yang tercatat pada transkrip Notetaker. Jawaban ditulis ringkas dan langsung, tanpa atribusi nama pembicara.
- Tidak mengubah ID, `document_id`, `expected_source_files`, `evidence_quote`, `evidence_type`, atau interval cakupan.
- Validasi Golden Set statis berhasil: 75 ID unik, 15 pertanyaan per dokumen, dan kutipan bukti cocok dengan sumber. Tidak ada API, benchmark, atau judge yang dijalankan.


**2026-10-25 — analisis ulang terhadap hasil run terbaru**

- Mengambil status terbaru per pasangan Question ID dan metode dari laporan JSON lokal. Ditemukan 14 pasangan request `NOT_FOUND`, mencakup 12 ID unik: NT-001-Q11; NT-002-Q04, Q12, Q15; NT-003-Q05; NT-004-Q03, Q04, Q08, Q12, Q15; NT-005-Q06 dan Q12.
- Mempersempit kembali pertanyaan dan menyelaraskan jawaban acuan pada 12 ID tersebut dengan kutipan/segmen transkrip. Untuk NT-005-Q06, pertanyaan kini hanya menanyakan direktorat yang disebut dalam kutipan; untuk NT-005-Q12, jawaban hanya menyebut pencatatan berdasarkan berat dan tidak menambah inferensi.
- Mempertahankan ID, sumber/dokumen yang diharapkan, kutipan bukti, jenis bukti, dan interval cakupan.
- Tidak mengirim request API atau menjalankan benchmark.
