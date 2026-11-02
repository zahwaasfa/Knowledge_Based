// ARCANA Unified Generic Schema - query inti terpadu.
// ---- Analitik taksonomi / sebaran ----
// A1. Rekap dokumen per kategori & sub-kategori
MATCH (d:Document)-[:IN_CATEGORY]->(s:SubCategory)-[:SUBCATEGORY_OF]->(c:Category)
RETURN c.name AS kategori, s.name AS sub_kategori, count(DISTINCT d) AS jumlah, collect(DISTINCT d.year)[..6] AS tahun ORDER BY jumlah DESC;

// A2. Sebaran dokumen per sub-kategori dan tahun
MATCH (d:Document)-[:IN_CATEGORY]->(s:SubCategory) RETURN s.name AS sub_kategori, d.year AS tahun, count(d) AS jumlah ORDER BY sub_kategori, tahun;

// A3. Rekap dampak infrastruktur: dokumen dampak per Tag berjenis infrastruktur
MATCH (d:Document {category:'Data Dampak'})-[:TAGGED_WITH]->(t:Tag {kind:'infrastruktur'})
RETURN t.name AS infrastruktur, count(d) AS dataset, collect(d.title)[..3] AS contoh ORDER BY dataset DESC;

// A4. Hierarki organisasi
MATCH (u:Organization)-[b:BELONGS_TO_ORG]->(p:Organization) RETURN p.name AS induk, p.level AS level_induk, collect(u.name)[..8] AS anggota, b.level_path AS jalur ORDER BY level_induk LIMIT 30;

// A5. Rujukan/regulasi/sumber data
MATCH (d:Document)-[b:TAGGED_WITH]->(r:Reference) RETURN r.title AS rujukan, b.role AS peran, count(d) AS dokumen ORDER BY dokumen DESC LIMIT 15;

// ---- Tanya-jawab & Graph Retrieval Grounding ----
// B1. Pertanyaan serupa (full-text) -> jawaban
CALL db.index.fulltext.queryNodes('question_text_ft', 'manfaat OR laporan OR kejadian') YIELD node, score
MATCH (node)-[:ANSWERED_BY]->(a:Answer) RETURN node.question_id AS id, node.text AS pertanyaan, a.text AS jawaban, score ORDER BY score DESC LIMIT 5;

// B2. Jawaban beserta sumber
MATCH (q:Question {question_id:'Q001'})-[:ANSWERED_BY]->(a:Answer) UNWIND a.cited_chunk_ids AS cid
MATCH (c:Chunk {chunk_id:cid}) MATCH (d:Document {doc_id:c.doc_id}) RETURN q.text AS pertanyaan, a.text AS jawaban, d.title AS dokumen, c.breadcrumb AS lokasi, c.page_number AS halaman;

// B3. Graph Traversal dengan Grounded Chunk Text (Menarik Teks Chunk Asli langsung dari Entitas untuk Anti-Halusinasi)
MATCH (e) WHERE (e:Tag OR e:Organization OR e:Reference OR e:Category) AND e.name IN $matched_entities
OPTIONAL MATCH (e)-[:MENTIONED_IN|TAGGED_WITH|BELONGS_TO_ORG]-(c1:Chunk)
OPTIONAL MATCH (e)-[r]-(target:Entity)-[:MENTIONED_IN|TAGGED_WITH|BELONGS_TO_ORG]-(c2:Chunk)
MATCH (d:Document {doc_id: coalesce(c1.doc_id, c2.doc_id)})
RETURN e.name AS source_entity, 
       type(r) AS relationship, 
       target.name AS target_entity, 
       d.title AS document_title, 
       collect(DISTINCT c1.text)[..3] + collect(DISTINCT c2.text)[..3] AS grounded_chunk_texts
LIMIT 10;

// B4. Tautan lintas dokumen antar chunk
MATCH (a:Chunk)-[r:REFERENCES_CHUNK]->(b:Chunk) WHERE a.doc_id <> b.doc_id
RETURN a.doc_id, a.breadcrumb, b.doc_id, b.breadcrumb, r.similarity, r.type ORDER BY r.similarity DESC LIMIT 10;

// B5. Validasi skema: label/relasi di luar skema terpadu (harus kosong)
CALL db.labels() YIELD label WHERE NOT label IN ['Document','Chunk','Category','SubCategory','Tag','Organization','Location','ProcessStep','Question','Answer','Reference'] RETURN 'LABEL' AS jenis, label AS nama
UNION
CALL db.relationshipTypes() YIELD relationshipType AS nama0 WHERE NOT nama0 IN ['CONTAINS_CHUNK','SUB_CHUNK_OF','IN_CATEGORY','SUBCATEGORY_OF','TAGGED_WITH','BELONGS_TO_ORG','LOCATED_IN','REFERENCES_CHUNK','CONTAINS_STEP','ASKED_ABOUT','ANSWERED_BY','MENTIONED_IN'] RETURN 'RELASI' AS jenis, nama0 AS nama;