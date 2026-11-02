"""Run a traceable Vector RAG vs Graph RAG evaluation. Never called by import."""
from __future__ import annotations
import argparse, csv, json, os, re, sys, time, urllib.error, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GOLDEN = ROOT / "evaluation" / "golden_set_notetaker_75.json"
RESULTS = ROOT / "evaluation" / "results"
try:
 from dotenv import load_dotenv
 load_dotenv(ROOT / ".env")
except ImportError:
 pass
METRICS = [
 ("Retrieval", "Precision@k", "Jumlah chunk hasil retrieval yang berasal dari dokumen yang diharapkan dibagi jumlah seluruh chunk yang di-retrieve; setiap chunk dihitung individual."),
 ("Retrieval", "Recall@k", "Jumlah dokumen relevan unik yang ditemukan dibagi jumlah dokumen relevan unik yang diharapkan."),
 ("Retrieval", "Mean Reciprocal Rank (MRR)", "Reciprocal rank posisi chunk relevan pertama; 0 bila tidak ditemukan."),
 ("Retrieval", "Hit Rate@k", "Proporsi pertanyaan yang memiliki minimal satu chunk relevan dalam top-k."),
 ("Generation", "Faithfulness", "Skor LLM-as-a-Judge 1-5 atas dukungan jawaban oleh konteks aktual yang dikirim ke LLM, disertai alasan JSON tervalidasi."),
 ("Generation", "Answer Correctness", "Skor LLM-as-a-Judge 1-5 dibanding jawaban acuan, memakai pertanyaan, jawaban acuan, jawaban hasil, dan konteks aktual."),
 ("Generation", "Citation Precision", "Jumlah sitasi yang benar-benar mendukung klaim dibagi seluruh sitasi; perlu pemeriksaan dukungan per sitasi."),
 ("Generation", "Citation Coverage", "Klaim faktual yang memiliki sitasi pendukung dibagi seluruh klaim faktual; perlu identifikasi dan review klaim."),
 ("Generation", "Answer Relevancy", "Skor LLM-as-a-Judge 1-5 tentang relevansi jawaban terhadap pertanyaan, dengan alasan JSON tervalidasi."),
 ("Operational", "Latency", "Waktu request query di sisi klien dalam milidetik; simpan juga latency server dan tahap retrieval/generation."),
 ("Operational", "Availability / Success Rate", "Request query sukses dibagi seluruh request yang dicoba; kegagalan teknis dipisahkan dari jawaban salah/tidak ditemukan."),
]

def sanitize(value):
 text=str(value)
 for key in ("GROQ_API_KEY","NEO4J_PASSWORD"):
  secret=os.getenv(key)
  if secret: text=text.replace(secret,"[REDACTED]")
 return text
def normfile(s): return (s or "").replace("\\", "/").rstrip("/").rsplit("/", 1)[-1].casefold()
def load_set(path):
 data=json.loads(path.read_text(encoding="utf-8"))
 if not isinstance(data,list): raise ValueError("Golden set harus berupa array JSON")
 return data

def validate_golden(data):
  errors=[]; ids=set(); counts={}; seenq=set(); sources_by_doc={}
 for n,row in enumerate(data,1):
  if not isinstance(row,dict): errors.append(f"baris {n}: item bukan object"); continue
  for key in ("id","document_id","question","expected_answer","expected_source_files","evidence_quote"):
   if key not in row or row[key] in (None, "", []): errors.append(f"{row.get('id',n)}: {key} kosong")
  q=(row.get("question") or "").strip().casefold()
  if q in seenq: errors.append(f"pertanyaan duplikat: {row.get('id')}")
  if q in seenq: errors.append(f"pertanyaan duplikat: {row.get('id')}")
  seenq.add(q)
  qid=row.get("id")
  if qid in ids: errors.append(f"ID duplikat: {qid}")
  ids.add(qid); doc=row.get("document_id"); counts[doc]=counts.get(doc,0)+1
  if not str(qid).startswith(str(doc)+"-"): errors.append(f"{qid}: prefix ID tidak cocok dengan document_id {doc}")
  sources=row.get("expected_source_files") or []
  if not isinstance(sources,list) or not sources: errors.append(f"{qid}: expected_source_files harus berisi minimal satu file")
  else:
   sources_by_doc.setdefault(doc,set()).update(normfile(src) for src in sources)
   for src in sources:
    if not (ROOT/"data"/"notetaker"/"markdown"/normfile(src)).is_file(): errors.append(f"{qid}: sumber tidak ditemukan: {src}")
  if not row.get("evidence_quote") or len(str(row["evidence_quote"]).strip())<12: errors.append(f"{qid}: evidence_quote terlalu pendek/kosong")
 if len(data)!=75: errors.append(f"jumlah pertanyaan {len(data)}, seharusnya 75")
 if len(ids)!=75: errors.append(f"jumlah ID unik {len(ids)}, seharusnya 75")
 expected={f"NT-{i:03d}":15 for i in range(1,6)}
 if counts!=expected: errors.append(f"distribusi document_id tidak sesuai: {counts}; seharusnya {expected}")
 if any(len(files)!=1 for files in sources_by_doc.values()) or len({next(iter(v)) for v in sources_by_doc.values() if v})!=5: errors.append(f"pemetaan expected_source_files tidak satu-ke-satu dengan lima dokumen: {sources_by_doc}")
 return errors,counts

def check_evidence(data):
 errors=[]
 for row in data:
  quote=" ".join(str(row.get("evidence_quote","")).split()).casefold()
  for src in row.get("expected_source_files",[]):
   p=ROOT/"data"/"notetaker"/"markdown"/normfile(src)
   source=" ".join(p.read_text(encoding="utf-8").split()).casefold() if p.is_file() else ""
   # Evidence can be a transcript excerpt with punctuation variation; allow a normalized exact substring only.
   q=re.sub(r"[^\w]+"," ",quote,flags=re.UNICODE).strip()
   s=re.sub(r"[^\w]+"," ",source,flags=re.UNICODE)
   if q and q not in s: errors.append(f"{row.get('id')}: evidence_quote tidak ditemukan persis setelah normalisasi di {src}")
 return errors

def get_json(url,timeout=15):
 with urllib.request.urlopen(url,timeout=timeout) as r: return json.loads(r.read().decode("utf-8"))
def request_json(url,payload,timeout,headers=None):
 raw=json.dumps(payload,ensure_ascii=False).encode("utf-8")
 req=urllib.request.Request(url,data=raw,headers={"Content-Type":"application/json", **(headers or {})})
 start=time.perf_counter()
 try:
  with urllib.request.urlopen(req,timeout=timeout) as r: status=r.status; body=r.read().decode("utf-8")
 except urllib.error.HTTPError as e:
  body=e.read().decode("utf-8","replace")[:2000]
  try: detail=json.loads(body)
  except Exception: detail={"message":body}
  raise RuntimeError(f"HTTP {e.code}: {json.dumps(detail,ensure_ascii=False)}") from e
 return json.loads(body),(time.perf_counter()-start)*1000,status

def retrieval_metrics(candidates,expected,k):
 exp={normfile(x) for x in expected if normfile(x)}; ranked=(candidates or [])[:k]
 hits=[normfile(x.get("file_name")) in exp and bool(x.get("file_name")) for x in ranked]
 unique={normfile(x.get("file_name")) for x,h in zip(ranked,hits) if h}
 first=next((i for i,h in enumerate(hits,1) if h),None)
 # Precision denominator counts returned chunks, including fewer than k if API returns fewer.
 return {"precision_at_k":sum(hits)/len(ranked) if ranked else None,
         "recall_at_k":len(unique)/len(exp) if exp else None,
         "mrr":1/first if first else 0.0,"hit_rate_at_k":1 if first else 0,
         "relevant_chunk_count":sum(hits),"retrieved_chunk_count":len(ranked),
         "relevant_unique_documents_found":sorted(unique),"expected_source_files":sorted(exp),"first_relevant_rank":first,
         "relevance_basis":"expected_source_files basename; individual retrieved chunks counted by their source filename"}

def atomic_json(path,obj):
 tmp=path.with_suffix(path.suffix+".tmp"); tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); tmp.replace(path)
def append_jsonl(path,obj):
 with path.open("a",encoding="utf-8") as f: f.write(json.dumps(obj,ensure_ascii=False,default=str)+"\n"); f.flush(); os.fsync(f.fileno())
def write_csv(path,rows,fields):
 with path.open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore"); w.writeheader(); w.writerows(rows)
def flush_progress(out,records):
 metric_rows=[]; chunk_rows=[]; manual=[]; errors=[]
 for r in records:
  m=r.get("retrieval_metrics") or {}; j=r.get("judge") or {}
  metric_rows.append({"Question ID":r["id"],"Document ID":r["document_id"],"Method":r["mode"],"Status":r.get("eval_status"),"Precision@k":m.get("precision_at_k"),"Recall@k":m.get("recall_at_k"),"MRR":m.get("mrr"),"Hit Rate@k":m.get("hit_rate_at_k"),"Faithfulness":j.get("faithfulness_score"),"Faithfulness reason":j.get("faithfulness_reason"),"Answer Correctness":j.get("answer_correctness_score"),"Correctness reason":j.get("answer_correctness_reason"),"Citation Precision":"MANUAL_REVIEW","Citation Coverage":"MANUAL_REVIEW","Answer Relevancy":j.get("answer_relevancy_score"),"Answer Relevancy reason":j.get("answer_relevancy_reason"),"Latency ms":r.get("client_latency_ms"),"Availability success":1 if r.get("success") else 0,"Generation success":1 if (r.get("generation") or {}).get("status")=="generated" else 0,"Run ID":r.get("evaluation_run_id")})
  for rank,c in enumerate(r.get("retrieved_candidates") or [],1): chunk_rows.append({"Question ID":r["id"],"Method":r["mode"],"Rank":rank,"Chunk ID":c.get("chunk_id"),"Document ID":c.get("doc_id"),"Source file":c.get("file_name"),"Score":c.get("score"),"Expected source":normfile(c.get("file_name")) in {normfile(x) for x in r["expected_source_files"]},"Retrieval methods":json.dumps(c.get("retrieval_methods") or [],ensure_ascii=False),"Snippet":c.get("snippet")})
  if not r.get("success") or r.get("eval_status") not in ("ANSWERED","PARTIAL") or j.get("status")!="scored" or any(j.get(k) is None for k in ("faithfulness_score","answer_correctness_score","answer_relevancy_score")): manual.append({"Question ID":r["id"],"Method":r["mode"],"Review item":"Review answer and evidence; judge failed, incomplete, or response needs review","Status":"PENDING","Run ID":r.get("evaluation_run_id")})
  manual.extend([{"Question ID":r["id"],"Method":r["mode"],"Review item":"Citation Precision: judge each cited source against the factual claim it supports","Status":"PENDING","Run ID":r.get("evaluation_run_id")},{"Question ID":r["id"],"Method":r["mode"],"Review item":"Citation Coverage: count factual claims and claims with supporting citation","Status":"PENDING","Run ID":r.get("evaluation_run_id")}])
  if j.get("status")=="scored": manual.append({"Question ID":r["id"],"Method":r["mode"],"Review item":"Verifikasi skor LLM-as-a-Judge against actual context and reference","Status":"SUGGESTED_AUDIT","Run ID":r.get("evaluation_run_id")})
  if (not r.get("success")) or r.get("eval_status") in ("RETRIEVAL_ERROR","LLM_ERROR","LLM_TIMEOUT","LLM_RATE_LIMIT"): errors.append({"Question ID":r["id"],"Method":r["mode"],"HTTP status":r.get("http_status"),"Status":r.get("eval_status"),"Generation status":(r.get("generation") or {}).get("status"),"Error":r.get("error") or (r.get("generation") or {}).get("error_message"),"Latency ms":r.get("client_latency_ms")})
 fields=["Question ID","Document ID","Method","Status","Precision@k","Recall@k","MRR","Hit Rate@k","Faithfulness","Faithfulness reason","Answer Correctness","Correctness reason","Citation Precision","Citation Coverage","Answer Relevancy","Answer Relevancy reason","Latency ms","Availability success","Generation success","Run ID"]
 write_csv(out/"metrics_per_request.csv",metric_rows,fields)
 write_csv(out/"retrieval_chunks.csv",chunk_rows,["Question ID","Method","Rank","Chunk ID","Document ID","Source file","Score","Expected source","Retrieval methods","Snippet"])
 write_csv(out/"manual_review_queue.csv",manual,["Question ID","Method","Review item","Status","Run ID"])
 write_csv(out/"errors.csv",errors,["Question ID","Method","HTTP status","Status","Generation status","Error","Latency ms"])

def request_body(item,mode,args):
 """Eksperimen "system": konfigurasi aktual apa adanya. "controlled": jumlah kandidat (top_k) dan anggaran karakter konteks sama,
 tanpa ekspansi tetangga untuk kedua metode (neighbor_window=0) sehingga hanya metode retrieval yang berbeda."""
 body={"question":item["question"],"top_k":args.top_k,"corpus":"notetaker","mode":mode,"debug":True,"include_graph":False}
 if getattr(args,"experiment","system")=="controlled": body.update(neighbor_window=0,context_chars=args.context_chars)
 return body

def judge_one(api_key,model,record,timeout):
 # Konteks EXACT yang dikirim ke LLM (termasuk tetangga SUB_CHUNK_OF) agar judge tidak menghukum klaim yang sah.
 ctx=(record.get("final_prompt") or {}).get("context_text") or record.get("context_sent_to_llm")
 if not record.get("success") or not record.get("answer") or ctx is None:
  return {"status":"not_scored","reason":"Successful answer and actual context sent to LLM are required."}
 schema={"faithfulness_score":"integer 1-5","faithfulness_reason":"string","answer_correctness_score":"integer 1-5","answer_correctness_reason":"string","answer_relevancy_score":"integer 1-5","answer_relevancy_reason":"string"}
 payload={"question":record["question"],"reference_answer":record.get("expected_answer"),"actual_context_sent_to_generation":ctx,"generated_answer":record.get("answer"),"response_schema":schema,
 "scoring":"Score each criterion independently from 1 to 5. Faithfulness measures support by actual context, correctness compares with reference answer, relevancy measures whether the answer addresses the question. Do not infer missing facts. Return only a JSON object matching schema. Give null score and reason if evidence is insufficient."}
 req={"model":model,"temperature":0,"response_format":{"type":"json_object"},"messages":[{"role":"system","content":"You are a conservative evaluator. Return valid JSON only. Never award a score based only on confident tone."},{"role":"user","content":json.dumps(payload,ensure_ascii=False)}]}
 try:
  body,ms,_=request_json("https://api.groq.com/openai/v1/chat/completions",req,timeout,{"Authorization":"Bearer "+api_key})
  obj=json.loads(body["choices"][0]["message"]["content"])
  keys=list(schema)
  if set(obj)!=set(keys): raise ValueError("judge JSON keys do not match schema")
  for key in ("faithfulness_score","answer_correctness_score","answer_relevancy_score"):
   v=obj[key]
   if v is not None and (isinstance(v,bool) or not isinstance(v,int) or not 1<=v<=5): raise ValueError(f"invalid {key}")
  for key in ("faithfulness_reason","answer_correctness_reason","answer_relevancy_reason"):
   if not isinstance(obj[key],str) or not obj[key].strip(): raise ValueError(f"missing {key}")
  return {"status":"scored","model":model,"latency_ms":round(ms,2),**obj}
 except Exception as e:
  return {"status":"judge_error","error":sanitize(f"{type(e).__name__}: {e}"),"scores":None}

def write_metrics_template(path):
 write_csv(path,[{"Dimensi":d,"Metrik":m,"Tujuan":o,"Nilai Vector RAG":"","Nilai Graph RAG":"","Status Penilaian":"Belum dinilai"} for d,m,o in METRICS], ["Dimensi","Metrik","Tujuan","Nilai Vector RAG","Nilai Graph RAG","Status Penilaian"])
def run(args):
 golden=load_set(Path(args.golden_set)); errors,counts=validate_golden(golden); evidence_errors=check_evidence(golden); errors+=evidence_errors
 if errors:
  saved=None
  if not args.validate_only:
   RESULTS.mkdir(parents=True,exist_ok=True); stamp=datetime.now().strftime("%Y%m%d_%H%M%S_%f"); failed=RESULTS/(args.session or ("validation_"+stamp)); failed.mkdir(parents=True,exist_ok=False)
   atomic_json(failed/"validation_error.json",{"status":"golden_validation_failed","checked_at":datetime.now(timezone.utc).isoformat(),"errors":errors,"golden_set":str(Path(args.golden_set).resolve())}); saved=failed
  print("Validasi gagal:",file=sys.stderr); [print("- "+x,file=sys.stderr) for x in errors]
  if saved: print(f"Detail tersimpan: {saved}",file=sys.stderr)
  return 2
 print(f"Golden set valid: {len(golden)} pertanyaan unik; 5 dokumen × 15; evidence_quote cocok dengan sumber.")
 if args.validate_only: return 0
 if args.limit is not None:
  if args.limit<1: print("--limit minimal 1",file=sys.stderr); return 2
  golden=golden[:args.limit]
 if args.top_k<1 or args.top_k>15: print("--top-k harus 1..15",file=sys.stderr); return 2
 api=args.api.rstrip("/")
 stamp=datetime.now().strftime("%Y%m%d_%H%M%S_%f")
 out=RESULTS/(args.session or stamp)
 out.mkdir(parents=True,exist_ok=False)
 base_config={"session_id":out.name,"created_at":datetime.now(timezone.utc).isoformat(),"api":api,"corpus":"notetaker","top_k":args.top_k,"experiment":args.experiment,"context_chars":args.context_chars if args.experiment=="controlled" else None,"modes":["vector","graph"],"request_order":"paired; alternating method order per question","questions":len(golden),"planned_rag_requests":len(golden)*2,"judge_enabled":not args.no_judge,"judge_model":args.judge_model if not args.no_judge else None,"golden_set":str(Path(args.golden_set).resolve()),"golden_set_sha256":__import__('hashlib').sha256(Path(args.golden_set).read_bytes()).hexdigest()}
 atomic_json(out/"config.json",base_config)
 write_metrics_template(out/"metric_matrix.csv")
 write_csv(out/"comparison_summary.csv",[],["Method","Successful requests","Attempted requests","Success rate","Precision@k","Recall@k","MRR","Hit Rate@k","Mean latency ms","Generation success rate","Faithfulness","Answer Correctness","Answer Relevancy","Citation Precision","Citation Coverage"])
 flush_progress(out,[])
 try:
  health=get_json(api+"/kb/health",min(args.timeout,20))
  problems=[]
  if health.get("status")!="ok" or health.get("neo4j")!="connected": problems.append("API/Neo4j tidak sehat")
  if health.get("llm")=="nonaktif": problems.append("USE_LLM/GROQ_API_KEY belum mengaktifkan layanan generasi")
  vr=health.get("vector_rag") or {}
  if not vr.get("configured"): problems.append("EMBEDDINGS=true belum aktif")
  if not vr.get("index_online"): problems.append("indeks chunk_embedding belum ONLINE")
  if not vr.get("embedded_chunks"): problems.append("belum ada chunk ber-embedding")
  expected_docs={f"NT-{i:03d}" for i in range(1,6)}
  notetaker_rows=((health.get("corpora") or {}).get("notetaker") or {}).get("documents") or []
  actual_docs={r.get("document_id") for r in notetaker_rows}
  missing=expected_docs-actual_docs
  if missing: problems.append(f"dokumen Notetaker belum lengkap: hilang {sorted(missing)}")
  incomplete=[r.get("document_id") for r in notetaker_rows if r.get("document_id") in expected_docs and (not r.get("chunks") or r.get("embedded_chunks")!=r.get("chunks"))]
  if incomplete: problems.append(f"chunk/embedding Notetaker belum lengkap: {sorted(incomplete)}")
  if str(os.getenv("GRAPH_RAG_USE_VECTOR", "false")).lower()=="true": problems.append("GRAPH_RAG_USE_VECTOR=true mencampur retrieval vector ke Graph RAG; set false untuk perbandingan ini")
  if not args.no_judge and not os.getenv("GROQ_API_KEY"): problems.append("GROQ_API_KEY belum diisi (atau gunakan --no-judge)")
  if problems: raise RuntimeError("; ".join(problems))
  base_config["health_at_start"]=health; atomic_json(out/"config.json",base_config)
  atomic_json(out/"preflight.json",{"status":"ready","checked_at":datetime.now(timezone.utc).isoformat(),"health":health})
 except Exception as e:
  failure=sanitize(f"{type(e).__name__}: {e}")
  atomic_json(out/"preflight.json",{"status":"failed","checked_at":datetime.now(timezone.utc).isoformat(),"error":failure})
  atomic_json(out/"run_summary.json",{"status":"preflight_failed","planned_requests":len(golden)*2,"saved_requests":0,"not_run_requests":len(golden)*2,"output_directory":str(out),"preflight_error":failure})
  print(f"Preflight gagal; tidak ada query dijalankan: {failure}; detail tersimpan di {out}",file=sys.stderr); return 2
 raw=out/"raw_requests.jsonl"; records=[]; failstreak=0; stopped=False
 print(f"Run: {out}\nKonfigurasi: {len(golden)} pertanyaan × 2 mode = {len(golden)*2} request; top_k={args.top_k}; judge={'aktif' if not args.no_judge else 'nonaktif'}.")
 for qi,item in enumerate(golden,1):
  # Alternate method order by question to reduce a fixed order effect while keeping paired settings identical.
  modes=("vector","graph") if qi%2 else ("graph","vector")
  for mode in modes:
   rec={"id":item["id"],"document_id":item["document_id"],"mode":mode,"question":item["question"],"expected_answer":item["expected_answer"],"expected_source_files":item["expected_source_files"],"evidence_quote":item["evidence_quote"],"top_k":args.top_k,"corpus":"notetaker","started_at":datetime.now(timezone.utc).isoformat(),"success":False,"run_status":"failed","error":None}
   t=time.perf_counter()
   try:
    result,client_ms,http_status=request_json(api+"/kb/query",request_body(item,mode,args),args.timeout)
    retrieval=result.get("retrieval") or {}; candidates=retrieval.get("candidate_chunks") or result.get("citations") or []; candidates=candidates[:args.top_k]
    debug=result.get("debug") or {}; sent=debug.get("context_sent_to_llm")
    rec.update({"success":True,"run_status":"completed","http_status":http_status,"answer":result.get("answer"),"eval_status":result.get("status"),"answer_mode":result.get("answer_mode"),"generation":result.get("generation"),"retrieval_trace":debug.get("retrieval_trace"),"retrieved_candidates":candidates,"context_sent_to_llm":sent,"final_prompt":debug.get("stage_3_4_final_prompt_sent_to_llm"),"llm_raw_answer":debug.get("stage_5_llm_raw_answer"),"citations":result.get("citations") or [],"validation":result.get("validation"),"evaluation_run_id":result.get("evaluation_run_id"),"timings_ms":result.get("timings_ms"),"server_latency_ms":result.get("latency_ms"),"client_latency_ms":round(client_ms,2),"retrieval_metrics":retrieval_metrics(candidates,item["expected_source_files"],args.top_k)})
    # Manual scores intentionally remain null; no heuristic is presented as a reviewed judgment.
    rec["manual_metrics"]={"citation_precision":None,"citation_coverage":None,"manual_review_required":True}
    if not args.no_judge: rec["judge"]=judge_one(os.getenv("GROQ_API_KEY",""),args.judge_model,rec,args.timeout)
   except Exception as e:
    rec["client_latency_ms"]=round((time.perf_counter()-t)*1000,2); rec["error"]=sanitize(f"{type(e).__name__}: {e}")
    rec["eval_status"]="LLM_RATE_LIMIT" if "429" in str(e) else "LLM_TIMEOUT" if "timed out" in str(e).lower() else "API_ERROR"
    rec["run_status"]="failed"
   append_jsonl(raw,rec); records.append(rec)
   flush_progress(out,records)
   atomic_json(out/"checkpoint.json",{"saved_requests":len(records),"planned_requests":len(golden)*2,"last_id":rec["id"],"last_mode":mode,"updated_at":datetime.now(timezone.utc).isoformat(),"status":"running"})
   print(f"[{len(records)}/{len(golden)*2}] {rec['id']} {mode}: {rec['run_status']} {rec.get('eval_status','')}",flush=True)
   failstreak=failstreak+1 if rec.get("eval_status") in ("LLM_TIMEOUT","LLM_RATE_LIMIT","LLM_ERROR") else 0
   if failstreak>=args.stop_after_llm_failures:
    stopped=True; print("Stop dini setelah kegagalan LLM berturut-turut; hasil tersimpan.",file=sys.stderr); break
   time.sleep(max(0,args.delay))
  if stopped: break

 # Per-question/method metrics and session comparison; no fabricated values.
 successful=[r for r in records if r.get("success")]
 grouped={m:[r for r in successful if r["mode"]==m] for m in ("vector","graph")}
 metric_rows=[]
 for r in records:
  m=r.get("retrieval_metrics") or {}; j=r.get("judge") or {}
  metric_rows.append({"Question ID":r["id"],"Document ID":r["document_id"],"Method":r["mode"],"Status":r.get("eval_status"),"Precision@k":m.get("precision_at_k"),"Recall@k":m.get("recall_at_k"),"MRR":m.get("mrr"),"Hit Rate@k":m.get("hit_rate_at_k"),"Faithfulness":j.get("faithfulness_score"),"Faithfulness reason":j.get("faithfulness_reason"),"Answer Correctness":j.get("answer_correctness_score"),"Correctness reason":j.get("answer_correctness_reason"),"Citation Precision":"MANUAL_REVIEW", "Citation Coverage":"MANUAL_REVIEW", "Answer Relevancy":j.get("answer_relevancy_score"),"Answer Relevancy reason":j.get("answer_relevancy_reason"),"Latency ms":r.get("client_latency_ms"),"Availability success":1 if r.get("success") else 0,"Generation success":1 if (r.get("generation") or {}).get("status")=="generated" else 0,"Run ID":r.get("evaluation_run_id")})
 write_csv(out/"metrics_per_request.csv",metric_rows,list(metric_rows[0]) if metric_rows else ["Question ID","Method"])
 chunk_rows=[]
 for r in records:
  for rank,c in enumerate(r.get("retrieved_candidates") or [],1):
   chunk_rows.append({"Question ID":r["id"],"Method":r["mode"],"Rank":rank,"Chunk ID":c.get("chunk_id"),"Document ID":c.get("doc_id"),"Source file":c.get("file_name"),"Score":c.get("score"),"Expected source":normfile(c.get("file_name")) in {normfile(x) for x in r["expected_source_files"]},"Retrieval methods":json.dumps(c.get("retrieval_methods") or [],ensure_ascii=False),"Snippet":c.get("snippet")})
 write_csv(out/"retrieval_chunks.csv",chunk_rows,["Question ID","Method","Rank","Chunk ID","Document ID","Source file","Score","Expected source","Retrieval methods","Snippet"])
 summary=[]
 for method, rs in grouped.items():
  summary.append({"Method":method,"Successful requests":len(rs),"Attempted requests":sum(r["mode"]==method for r in records),"Success rate":len(rs)/sum(r["mode"]==method for r in records) if any(r["mode"]==method for r in records) else None,
  **{label:(mean([r["retrieval_metrics"][key] for r in rs if r.get("retrieval_metrics",{}).get(key) is not None]) if any(r.get("retrieval_metrics",{}).get(key) is not None for r in rs) else None) for label,key in (("Precision@k","precision_at_k"),("Recall@k","recall_at_k"),("MRR","mrr"),("Hit Rate@k","hit_rate_at_k"))},
  "Mean latency ms":mean([r["client_latency_ms"] for r in rs]) if rs else None,
  "Generation success rate":sum(1 for r in rs if (r.get("generation") or {}).get("status")=="generated")/len(rs) if rs else None,
  **{label:(mean([r["judge"][key] for r in rs if isinstance((r.get("judge") or {}).get(key),int)]) if any(isinstance((r.get("judge") or {}).get(key),int) for r in rs) else None) for label,key in (("Faithfulness","faithfulness_score"),("Answer Correctness","answer_correctness_score"),("Answer Relevancy","answer_relevancy_score"))},
  "Citation Precision":"manual review required","Citation Coverage":"manual review required"})
 write_csv(out/"comparison_summary.csv",summary,list(summary[0]) if summary else ["Method"])
 manual=[]
 for r in records:
  if not r.get("success") or r.get("eval_status") not in ("ANSWERED","PARTIAL") or not (r.get("judge") or {}).get("status")=="scored" or any((r.get("judge") or {}).get(k) is None for k in ("faithfulness_score","answer_correctness_score","answer_relevancy_score")):
   manual.append({"Question ID":r["id"],"Method":r["mode"],"Review item":"Review answer and evidence; judge failed, incomplete, or request failed","Status":"PENDING","Run ID":r.get("evaluation_run_id")})
  manual.append({"Question ID":r["id"],"Method":r["mode"],"Review item":"Citation Precision: judge each cited source against the factual claim it supports","Status":"PENDING","Run ID":r.get("evaluation_run_id")})
  manual.append({"Question ID":r["id"],"Method":r["mode"],"Review item":"Citation Coverage: count factual claims and claims with supporting citation","Status":"PENDING","Run ID":r.get("evaluation_run_id")})
  if (r.get("judge") or {}).get("status")=="scored": manual.append({"Question ID":r["id"],"Method":r["mode"],"Review item":"Verifikasi skor LLM-as-a-Judge against actual context and reference","Status":"SUGGESTED_AUDIT","Run ID":r.get("evaluation_run_id")})
 write_csv(out/"manual_review_queue.csv",manual,["Question ID","Method","Review item","Status","Run ID"])
 write_metrics_template(out/"metric_matrix.csv")
 errors=[r for r in records if (not r.get("success")) or r.get("eval_status") in ("RETRIEVAL_ERROR","LLM_ERROR","LLM_TIMEOUT","LLM_RATE_LIMIT")]
 write_csv(out/"errors.csv",[{"Question ID":r["id"],"Method":r["mode"],"HTTP status":r.get("http_status"),"Status":r.get("eval_status"),"Generation status":(r.get("generation") or {}).get("status"),"Error":r.get("error") or (r.get("generation") or {}).get("error_message"),"Latency ms":r.get("client_latency_ms")} for r in errors],["Question ID","Method","HTTP status","Status","Generation status","Error","Latency ms"])
 finished={"status":"stopped_early" if stopped else "completed","finished_at":datetime.now(timezone.utc).isoformat(),"saved_requests":len(records),"planned_requests":len(golden)*2,"successful_requests":len(successful),"failed_requests":sum(1 for r in records if not r.get("success")),"operational_error_records":len(errors),"not_run_requests":len(golden)*2-len(records),"judge_calls":sum(1 for r in records if "judge" in r),"manual_review_items":len(manual),"output_directory":str(out)}
 atomic_json(out/"checkpoint.json",finished); atomic_json(out/"run_summary.json",finished)
 print(json.dumps(finished,ensure_ascii=False,indent=2)); return 0 if len(successful)==len(records) and not stopped else 1

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--api",default=os.getenv("KB_API_URL","http://localhost:8001")); p.add_argument("--golden-set",default=str(DEFAULT_GOLDEN)); p.add_argument("--top-k",type=int,default=5); p.add_argument("--timeout",type=int,default=300); p.add_argument("--delay",type=float,default=1.0); p.add_argument("--stop-after-llm-failures",type=int,default=5); p.add_argument("--judge-model",default=os.getenv("GROQ_MODEL_NAME","openai/gpt-oss-120b")); p.add_argument("--no-judge",action="store_true",help="Skip optional automatic LLM-as-a-Judge calls."); p.add_argument("--limit",type=int,default=None,help="Run first N questions only; separate smoke mode."); p.add_argument("--validate-only",action="store_true",help="Validate golden set and source evidence, without calling API."); p.add_argument("--experiment",choices=("system","controlled"),default="system",help="system=konfigurasi aktual; controlled=top_k & anggaran konteks sama, tanpa tetangga. Jangan menggabungkan hasil keduanya."); p.add_argument("--context-chars",type=int,default=12000); p.add_argument("--session",default=None,help="Optional new session folder name; must not already exist.")
 a=p.parse_args()
 try:return run(a)
 except KeyboardInterrupt:return 130
if __name__=="__main__": raise SystemExit(main())
