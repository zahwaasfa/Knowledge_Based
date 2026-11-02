# Audit & optimasi Graph RAG ARCANA (28 Okt 2026)

Status: **kode diperbaiki dan lulus 34 uji offline; dampak pada metrik BELUM terbukti** — lingkungan audit tidak memiliki Neo4j/Groq, sehingga evaluasi ulang end-to-end harus dijalankan di lingkungan Anda (perintah di bagian 5). Baseline (`rag_evaluation_20261024_RAPI.xlsx`, `reports/*`) tidak diubah.

## 1. Temuan (terbukti dari kode + log 150 kasus)
| # | Temuan | Bukti | Status |
|---|---|---|---|
| T1 | Batas keras `per_doc >= 3` di `search.search_chunks` menghentikan seleksi pada ≤3 chunk/dokumen. Korpus notetaker = 1 dokumen/pertanyaan. | Trace: `fused_candidates=60` pada 70/75 kasus, tetapi chunk dikembalikan rata-rata 3,16; 44 kasus tepat 3 chunk dari satu dokumen; Vector rata-rata 4,92. P@k ketat = relevan/5, jadi maksimum Graph ≈0,6. | **Akar masalah utama P@k ketat** |
| T2 | Filter korpus tidak diterapkan pada `entity_docs`, `expand_graph`, `CHUNK_LEXICAL` (jalur `graph_entity_document_chunks`). | Run memakai `corpus=notetaker`, namun 49 dari 70 chunk Graph yang tidak relevan berasal dari `DOC-*` (korpus Bappenas). Semua 51 chunk jalur graf-entitas tidak relevan (0%). Tanpa kebocoran, P chunk Graph = 0,888 (167/188), bukan 0,785 (batas atas deskriptif, bukan prediksi). | **Terbukti** |
| T3 | Log/judge tidak melihat konteks yang sama dengan LLM: LLM menerima `neighbors` (SUB_CHUNK_OF ±1), tetapi `context_to_text` & workbook hanya mencatat `text`. | Alasan judge Graph: "kalimat pendukung persisnya tidak terlihat pada cuplikan konteks tercatat". Faithfulness Graph ≤3 pada 22 kasus vs 10 Vector. | **Terbukti (bias pengukuran)**; besarnya efek tidak dapat dihitung tanpa rerun |
| T4 | Alasan judge juga menyebut klaim pembuka/elaborasi yang tidak tertulis di sumber ("salah tafsir", "elaborasi … tidak didukung"). | NT-002-Q07, Q08, NT-001-Q08/Q09. | Hipotesis kuat; diuji lewat aturan prompt 9 |
| T5 | Bias Faithfulness=5 pada abstain: nyata tetapi **kecil**. | Non-abstain: Graph 4,096 vs Vector 4,523 (Δ −0,43; semua: 4,12 vs 4,59). Selisih tetap ada. Pada 64 pasangan non-abstain-keduanya Δ −0,39, Wilcoxon p_holm 0,008, tetapi CI95 klaster [−0,92; +0,06] memuat 0. | Terbukti |
| T6 | "Graph" pada korpus notetaker praktis = full-text + resolusi dokumen + tetangga transkrip. Skema hanya memiliki Document/Chunk/Tag/Organization/Reference/Category; **tidak ada node Aktor/Keputusan/TindakLanjut** (hanya NT-002 punya bagian "Keputusan Penting"/"Daftar Tindak Lanjut" sebagai teks). | `ingest.py` MERGE labels; Golden Set 75 = pertanyaan satu-fakta per interval waktu. | Golden Set belum menguji kemampuan khas KG |
| T7 | Abstain Graph 2/75 vs Vector 10/75 bukan keunggulan graf per se: pada 3 pertanyaan Vector tidak menemukan dokumen (NT-002-Q05/Q13/Q15) ia abstain/parsial. Jangan dikreditkan ke relasi graf. | Raw Retrieval. | Terbukti |
| T8 | Latency Graph median 5,6 s vs 4,5 s; belum terkontrol (urutan, cache, rate limit). Neighbor query + 3 jalur graf menambah round-trip. | Workbook. | Terukur, tak terkontrol |

Reproduksi angka Anda dari workbook: seluruh rata-rata (3,493/2,867; 4,68/4,333; 4,12/4,587; 0,445/0,805; 0,785/0,817; MRR 0,942/0,900; 3,16/4,92; abstain 2/10) cocok.

## 2. Perubahan kode (minimal, kompatibel API/UI)
- `kb/search.py`: (a) filter `$corpus` pada `CHUNK_LEXICAL`, `expand_graph`, `entity_docs`; (b) `select_top()` baru: skor sama seperti sebelumnya, **dedup teks identik**, buang kandidat yang HANYA dari jalur entitas graf bila memuat <20% istilah topik (tidak pernah mengosongkan hasil), seleksi **dua lintasan** (keragaman dokumen cap 3, lalu *backfill* hingga top_k); (c) `rrf(weights=…)`, bobot jalur entitas 0,5; (d) `restrict_doc_ids` benar-benar membatasi ke dokumen hasil resolusi (fallback bila kosong).
- `kb/retrieval.py`: memakai `GRAPH_RESTRICT_TO_RESOLVED`; parameter `neighbor_window` opsional.
- `kb/rag.py`: aturan prompt 9 (tanpa tafsir/elaborasi; label tetangga = bukti sah) — **prompt yang sama untuk kedua metode**, dapat dimatikan `LLM_STRICT_GROUNDING=false`; `generate(max_context_chars=…)`. Model `openai/gpt-oss-120b`, provider, kredensial tidak diubah.
- `kb_api/main.py`: field opsional `neighbor_window`, `context_chars` (default None = perilaku lama; respons tidak berubah).
- `kb/config.py`: `GRAPH_PER_DOC_CAP=3`, `GRAPH_ENTITY_RRF_WEIGHT=0.5`, `GRAPH_MIN_COVERAGE=0.2`, `GRAPH_RESTRICT_TO_RESOLVED=true`, `LLM_STRICT_GROUNDING=true`.
- `scripts/evaluate_rag.py`, `scripts/export_eval_workbook.py`: konteks yang dicatat kini memuat tetangga (identik dengan yang dikirim). `evaluation/run_full_evaluation.py`: judge memakai `final_prompt.context_text` (EXACT), `--experiment system|controlled`, `--context-chars`.
- Baru: `evaluation/compare_runs.py` (analisis berpasangan, Holm, CI bootstrap & klaster, per dokumen, non-abstain), `tests/test_graph_selection.py` (7 uji), `evaluation/golden_set_kg_extension_PROPOSAL.json`.
- Tidak dilakukan (belum ada bukti): menaikkan top-k/kedalaman traversal; reranker lintas-encoder; membangun node Aktor/Keputusan (butuh persetujuan Anda: perubahan skema/ingest).

## 3. Alur retrieval setelah optimasi
```
pertanyaan → analyze (intent, topik) → find_documents (FT + katalog) → pick_resolved (cover ≥0,4)
  → search_chunks:
      fulltext chunk (corpus-filtered) ─┐
      jalur graf: Tag/Org/Ref/Category→Chunk, entity_docs, expand_graph(TAGGED_WITH), lexical-doc (semua corpus-filtered) ─┤ RRF (bobot graf 0,5)
      [vector opsional, GRAPH_RAG_USE_VECTOR] ─┘
      → batasi ke dokumen resolusi (fallback bila kosong) → cov leksikal → select_top: dedup, drop graph-only cov<0,2, lintasan-1 (cap 3/dok), lintasan-2 backfill → top_k
  → tetangga SUB_CHUNK_OF (window 1) → select_context (anggaran 12k karakter) → LLM (1 panggilan) → validasi/finalisasi sitasi
log evaluasi = prompt.context_text yang sama dengan yang dikirim
```

## 4. Desain eksperimen (jangan dicampur)
1. **Sistem aktual**: `--experiment system` (default): konfigurasi apa adanya; Graph memakai tetangga.
2. **Retrieval terkontrol**: `--experiment controlled`: top_k sama, anggaran konteks sama (`--context-chars`), `neighbor_window=0` untuk kedua metode.
Pertanyaan, dokumen, jawaban acuan, model, judge, prompt sama; urutan metode bergantian per pertanyaan (sudah ada). Simpan `golden_set_sha256`, konfigurasi (`Run Config`) dan commit. Ablasi satu-faktor lewat env: `GRAPH_PER_DOC_CAP`, `GRAPH_ENTITY_RRF_WEIGHT=1.0`, `GRAPH_MIN_COVERAGE=0`, `GRAPH_RESTRICT_TO_RESOLVED=false`, `LLM_STRICT_GROUNDING=false`.
Catatan: prompt baru (aturan 9) dan konteks-judge baru mengubah definisi pengukuran untuk **kedua** metode, sehingga **Vector RAG juga harus dijalankan ulang** sebagai baseline-v2; jangan membandingkan Graph-baru dengan Vector-lama pada Faithfulness.

## 5. Perintah (jalankan di lingkungan Anda; baseline tidak ditimpa karena tiap run membuat folder sesi baru)
```bash
python -m pytest -q tests                      # uji offline (butuh dependensi proyek)
python -m scripts.run_schema                   # TIDAK diperlukan; tidak ada perubahan skema/data Neo4j
# (re)start API dengan kode baru, lalu:
python evaluation/run_full_evaluation.py --api http://localhost:8001 --top-k 5 --experiment system     --session opt_system_v2
python evaluation/run_full_evaluation.py --api http://localhost:8001 --top-k 5 --experiment controlled --context-chars 12000 --session opt_controlled_v2
# ekspor workbook (skrip yang sudah ada) lalu bandingkan:
python evaluation/compare_runs.py --a <baseline.xlsx> --b <opt_system_v2.xlsx>  --out evaluation/results/analysis_system_v2
python evaluation/compare_runs.py --a <baseline.xlsx> --b <opt_controlled_v2.xlsx> --out evaluation/results/analysis_controlled_v2   # hanya bila baseline controlled tersedia; kalau tidak, jalankan baseline controlled dengan kode lama
curl -s localhost:8001/kb/health   # model: groq:openai/gpt-oss-120b
```
Tolok ukur keberhasilan (hipotesis, belum diuji): chunk dikembalikan → ≈5; P@k ketat Graph mendekati P chunk (≥0,7); 0 chunk `DOC-*` pada corpus=notetaker; Faithfulness Graph tidak turun; abstain tidak naik.


docker compose run --rm loader python scripts/evaluate_rag.py --api http://kb-api:8000 --corpus notetaker --golden-set evaluation/golden_set_notetaker_75.json --mode both --ids NT-004-Q01,NT-004-Q02,NT-004-Q03,NT-004-Q04,NT-004-Q05 --delay 40 --append-workbook --replace-existing-ids --workbook-output reports/rag_evaluation_20261028_131028_743448.xlsx


## 6. Belum terselesaikan / keterbatasan
- Efek perubahan pada Faithfulness/Correctness belum diukur (perlu rerun Groq). Citation Precision/Coverage dan Evidence recall leksikal tetap memerlukan penilaian manual/data yang tidak ada di workbook (`compare_runs.py` hanya menghitung Source accuracy tingkat file).
- Relevansi = kecocokan file sumber (tingkat dokumen). Pada korpus 1-dokumen-per-pertanyaan, Hit@k/Recall@k nyaris tak membedakan metode; label relevansi tingkat chunk/timestamp diperlukan untuk menilai kualitas chunk sebenarnya.
- 75 pertanyaan tersarang dalam 5 dokumen: p-value indikatif; CI klaster lebih lebar (mis. Faithfulness Δ −0,47, CI klaster [−0,91; −0,07]; non-abstain [−0,92; +0,06]).
- Skema belum memodelkan aktor/keputusan/tindak lanjut; manfaat relasi KG pada pertanyaan multi-hop belum dapat diuji dengan Golden Set 75. Usulan 6 pertanyaan (NT-002, kutipan terverifikasi persis terhadap sumber, perlu tinjauan manusia) ada di `golden_set_kg_extension_PROPOSAL.json`; kategori yang perlu ditambah untuk NT-001/003/004/005: aktor→tindak lanjut, keputusan→alasan, lintas-bagian, multi-hop aktor→proses→unit, dan pertanyaan negatif (informasi memang tidak ada). Langkah berikut (butuh persetujuan): ekstraksi entitas LLM yang divalidasi manusia → node `Person/Decision/ActionItem` + relasi `ASSIGNED_TO/DECIDED_IN/FOLLOWS_UP`, tanpa mengubah korpus.
- `tests/test_api_flow.py` tidak dapat dijalankan di sini (fastapi tidak terpasang); `main.py` hanya lulus pemeriksaan sintaks.
