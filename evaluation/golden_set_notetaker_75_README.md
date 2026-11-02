# Golden set notetaker: 75 pertanyaan

File `golden_set_notetaker_75.json` berisi 15 pertanyaan dan jawaban untuk masing-masing transkrip NT-001 sampai NT-005. Setiap item menggunakan skema yang dapat dibaca oleh `scripts/evaluate_rag.py`, termasuk `expected_source_files` dan `evidence_quote`.

## Cakupan sumber

Berkas sumber yang tersedia adalah transkrip Markdown dan ekspor JSON. Keduanya tidak menyimpan penanda halaman atau pemetaan timestamp-ke-halaman, sehingga nomor halaman yang disebut pada permintaan tidak dapat diverifikasi dari berkas ini. Atas arahan pengguna, cakupan dibuat berdasarkan waktu: durasi tiap transkrip dibagi menjadi 15 interval berurutan dengan panjang hampir sama, dari `00:00:00` sampai akhir durasi pada metadata Markdown. `coverage_time_start` dan `coverage_time_end` menunjukkan interval cakupan sampling pertanyaan, bukan klaim bahwa kutipan bukti berasal tepat dari batas waktu tersebut. Kutipan bukti tetap diambil dari teks sumber; untuk transkrip dengan ringkasan terstruktur, beberapa kutipan berasal dari bagian ringkasan dan ditandai `evidence_type: summary`.

Karena interval sampling bukan halaman, set ini tidak membuktikan cakupan tiap halaman asli. Untuk menguji cakupan halaman secara literal, diperlukan PDF atau dokumen dengan pemisah halaman yang dapat dipetakan ke transkrip.

## Menjalankan evaluasi

Gunakan runner dan prasyarat dalam [`RUNBOOK.md`](RUNBOOK.md): `python evaluation/run_full_evaluation.py`. Pertanyaan golden set diperbarui agar tidak menanyakan atribusi kepada nama pembicara. Semua 32 ID unik yang masih berstatus NOT_FOUND pada laporan tersimpan terbaru ditinjau ulang dan pertanyaan/jawaban acuannya ditulis berdasarkan transkrip. ID dan pemetaan sumber tetap; rinciannya ada di `GOLDEN_SET_CHANGELOG.md`. Validasi statis golden set telah lolos. Perubahan redaksi belum membuktikan status NOT_FOUND akan teratasi; lakukan rerun terbatas setelah layanan siap.

Evaluasi memerlukan API dan konfigurasi model yang aktif. Pembuatan dataset ini sendiri tidak menjalankan atau mengklaim hasil evaluasi retrieval/LLM.
