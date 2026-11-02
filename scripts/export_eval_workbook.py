"""Export one complete multi-sheet ARCANA evaluation workbook from a real report JSON."""
from __future__ import annotations
import argparse, json, re, shutil
from pathlib import Path
from copy import copy
from statistics import mean
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter

NAVY="17365D"; BLUE="D9EAF7"; PALE="F3F6FA"; WHITE="FFFFFF"; GRAY="D9E1F2"
THIN=Side(style="thin",color="D9E1F2")
METRICS=[
 ("Retrieval","Precision@k","Jumlah chunk dari dokumen yang diharapkan dibagi seluruh chunk yang di-retrieve; setiap chunk dihitung individual.","precision"),
 ("Retrieval","Recall@k","Jumlah dokumen relevan unik yang ditemukan dibagi jumlah dokumen relevan unik yang diharapkan.","recall"),
 ("Retrieval","Mean Reciprocal Rank (MRR)","Reciprocal rank chunk relevan pertama; 0 bila tidak ditemukan.","mrr"),
 ("Retrieval","Hit Rate@k","Proporsi pertanyaan dengan minimal satu chunk relevan dalam top-k.","hit"),
 ("Generation","Faithfulness","Skor LLM-as-a-Judge 1–5 tentang dukungan jawaban oleh konteks aktual, dengan alasan.","faithfulness"),
 ("Generation","Answer Correctness","Skor LLM-as-a-Judge 1–5 dibanding jawaban acuan dan konteks aktual, dengan alasan.","correctness"),
 ("Generation","Citation Precision","Sitasi yang benar-benar mendukung klaim dibagi seluruh sitasi; memerlukan review bukti.","citation_precision"),
 ("Generation","Citation Coverage","Klaim faktual dengan sitasi pendukung dibagi seluruh klaim faktual; memerlukan review.","citation_coverage"),
 ("Generation","Answer Relevancy","Skor LLM-as-a-Judge 1–5 tentang relevansi jawaban terhadap pertanyaan, dengan alasan.","answer_relevancy"),
 ("Operational","Latency","Waktu request; laporkan rata-rata milidetik dan simpan latency per request.","latency"),
 ("Operational","Availability / Success Rate","Request endpoint berhasil dibagi request yang dicoba; pisahkan dari kualitas jawaban.","availability"),
]
def txt(v,limit=32000):
 if v is None: return None
 if isinstance(v,(dict,list)): v=json.dumps(v,ensure_ascii=False,default=str)
 s=str(v); s="".join(ch for ch in s if ch in "\t\n\r" or ord(ch)>=32 and not 0xD800<=ord(ch)<=0xDFFF)
 return s[:limit]
def basename(s): return (s or "").replace("\\","/").rstrip("/").rsplit("/",1)[-1].casefold()
def rows_from(evaluation): return evaluation.get("results") or []
def metric_values(row):
 m=row.get("retrieval_metrics") or {}; old=row.get("document_match_proxy") or {}
 return {
  "precision":m.get("precision_at_k",old.get("precision_at_k_expected_file_proxy")),
  "recall":m.get("recall_at_k",old.get("recall_at_k_expected_unique_file_proxy")),
  "mrr":m.get("mrr",old.get("mrr_expected_file_proxy")),
  "hit":m.get("hit_rate_at_k",old.get("hit_rate_at_k_expected_file_proxy")),
 }
def average(vals):
 nums=[v for v in vals if isinstance(v,(int,float)) and not isinstance(v,bool)]
 return mean(nums) if nums else None
def style_sheet(ws,widths=None,filter_sheet=True):
 ws.sheet_view.showGridLines=False
 ws.freeze_panes="A2"
 if ws.max_row>=1 and ws.max_column>=1:
  for cell in ws[1]:
   cell.fill=PatternFill("solid",fgColor=NAVY); cell.font=Font(color=WHITE,bold=True)
   cell.alignment=Alignment(vertical="center",wrap_text=True)
   cell.border=Border(bottom=THIN)
  ws.row_dimensions[1].height=34
  if filter_sheet and ws.max_row>1: ws.auto_filter.ref=ws.dimensions
  for row in ws.iter_rows(min_row=2):
   for c in row:
    c.alignment=Alignment(vertical="top",wrap_text=True)
    c.border=Border(bottom=THIN)
   if row[0].row%2==0:
    for c in row: c.fill=PatternFill("solid",fgColor=PALE)
  for col in range(1,ws.max_column+1):
   letter=get_column_letter(col)
   ws.column_dimensions[letter].width=(widths or {}).get(letter, min(max(14,max(len(str(ws.cell(1,col).value or ""))+2,18)),40))
def add_table_sheet(wb,name,headers,rows,widths=None):
 ws=wb.create_sheet(name); ws.append(headers)
 for row in rows: ws.append([txt(v) if isinstance(v,(dict,list)) else v for v in row])
 style_sheet(ws,widths)
 return ws
def error_for(r):
 gen=r.get("generation") or {}; status=str(r.get("eval_status") or "")
 return (not r.get("success",False)) or status in {"RETRIEVAL_ERROR","LLM_ERROR","LLM_TIMEOUT","LLM_RATE_LIMIT","API_ERROR"} or gen.get("status") in {"failed","disabled"}
def judge_of(r): return r.get("judge") or r.get("judge_result") or {}
DATA_SHEETS=("Matriks Metrik","Permintaan","Retrieval Detail","Konteks LLM","Trace","Log Error","Review Manual","Konfigurasi")
REMOVED_SHEETS=("Survei SUS","Pertanyaan SUS")   # SUS tidak lagi bagian evaluasi; sheet lama dibuang saat append
def copy_sheet(source, target):
 for row in source.iter_rows():
  for cell in row:
   dst=target.cell(cell.row,cell.column,cell.value)
   if cell.has_style: dst._style=copy(cell._style)
   if cell.number_format: dst.number_format=cell.number_format
   if cell.alignment: dst.alignment=copy(cell.alignment)
   if cell.font: dst.font=copy(cell.font)
   if cell.fill: dst.fill=copy(cell.fill)
   if cell.border: dst.border=copy(cell.border)
   if cell.protection: dst.protection=copy(cell.protection)
 for key,dim in source.column_dimensions.items(): target.column_dimensions[key].width=dim.width
 for key,dim in source.row_dimensions.items(): target.row_dimensions[key].height=dim.height
 for merged in source.merged_cells.ranges: target.merge_cells(str(merged))
 target.freeze_panes=source.freeze_panes
 target.sheet_view.showGridLines=source.sheet_view.showGridLines

def summary_history_row(ws,session):
 meta={ws.cell(r,1).value:ws.cell(r,2).value for r in range(3,13)}
 methods={}
 for r in range(17,19):
  name=ws.cell(r,1).value
  if name: methods[name]={"tried":ws.cell(r,2).value,"success":ws.cell(r,3).value,"rate":ws.cell(r,4).value,"latency_ms":ws.cell(r,6).value}
 return [session,meta.get("Waktu run"),meta.get("Golden set"),meta.get("Top-k"),meta.get("Pertanyaan dijalankan"),meta.get("Target request"),meta.get("Request tercatat"),meta.get("Request gagal"),meta.get("Belum dijalankan"),meta.get("Catatan"),json.dumps(methods,ensure_ascii=False)]

def initialize_cumulative(current, session):
 hist=current.create_sheet("Riwayat Run")
 hist.append(["Session ID","Waktu run","Golden set","Top-k","Pertanyaan dijalankan","Target request","Request tercatat","Request gagal","Belum dijalankan","Catatan","Ringkasan metode (JSON)"])
 hist.append(summary_history_row(current["Ringkasan"],session))
 style_sheet(hist,{"A":34,"B":28,"C":72,"D":12,"E":22,"F":18,"G":18,"H":18,"I":18,"J":60,"K":78})
 for name in DATA_SHEETS:
  ws=current[name]; ws.insert_cols(1); ws.cell(1,1,"Session ID")
  for row in range(2,ws.max_row+1): ws.cell(row,1,session)
  ws.column_dimensions["A"].width=32; ws.auto_filter.ref=ws.dimensions; ws.freeze_panes="A2"
  ws.cell(1,1).fill=PatternFill("solid",fgColor=NAVY); ws.cell(1,1).font=Font(color=WHITE,bold=True); ws.cell(1,1).alignment=Alignment(vertical="center",wrap_text=True)
 return current

def append_session(existing, current, output, session, evaluation, replace_existing_ids=False):
 legacy=session
 if "Riwayat Run" not in existing.sheetnames:
  hist=existing.create_sheet("Riwayat Run")
  hist.append(["Session ID","Waktu run","Golden set","Top-k","Pertanyaan dijalankan","Target request","Request tercatat","Request gagal","Belum dijalankan","Catatan","Ringkasan metode (JSON)"])
  if "Ringkasan" in existing.sheetnames: hist.append(summary_history_row(existing["Ringkasan"],"legacy_existing_workbook"))
 else: hist=existing["Riwayat Run"]
 hist.append(summary_history_row(current["Ringkasan"],session))
 style_sheet(hist,{"A":34,"B":28,"C":72,"D":12,"E":22,"F":18,"G":18,"H":18,"I":18,"J":60,"K":78})
 # Replace old detail rows for IDs rerun in this session, keeping unrelated questions.
 replacing={str(r.get("id")) for r in rows_from(evaluation) if r.get("id")} if replace_existing_ids else set()
 if replacing:
  for name in ("Permintaan","Retrieval Detail","Konteks LLM","Trace","Log Error","Review Manual"):
   if name not in existing.sheetnames: continue
   ws=existing[name]
   if ws.cell(1,1).value!="Session ID":
    ws.insert_cols(1); ws.cell(1,1,"Session ID")
    ws.cell(1,1).fill=PatternFill("solid",fgColor=NAVY); ws.cell(1,1).font=Font(color=WHITE,bold=True)
   # These sheets all use Question ID as the second column after Session ID.
   for row in range(ws.max_row,1,-1):
    if str(ws.cell(row,2).value or "") in replacing: ws.delete_rows(row)
 # Append detail rows in a single set of sheets, tagging every row by session.
 for name in DATA_SHEETS:
  src=current[name]
  if name not in existing.sheetnames:
   dst=existing.create_sheet(name)
   for row in src.iter_rows():
    dst.append([session]+[c.value for c in row])
   style_sheet(dst)
   continue
  dst=existing[name]
  if dst.cell(1,1).value!="Session ID":
   dst.insert_cols(1)
   dst.cell(1,1,"Session ID")
   dst.cell(1,1).fill=PatternFill("solid",fgColor=NAVY); dst.cell(1,1).font=Font(color=WHITE,bold=True); dst.cell(1,1).alignment=Alignment(vertical="center",wrap_text=True)
   for r in range(2,dst.max_row+1): dst.cell(r,1,legacy)
   dst.column_dimensions["A"].width=32
  # Header must match after the session column has been introduced.
  source_headers=[c.value for c in src[1]]
  target_headers=[dst.cell(1,c).value for c in range(2,dst.max_column+1)]
  if source_headers!=target_headers:
   raise RuntimeError(f"Struktur sheet {name} berbeda; workbook lama tidak diubah.")
  for source_row in src.iter_rows(min_row=2,values_only=False):
   values=[session]+[c.value for c in source_row]
   dst.append(values)
   newrow=dst.max_row
   template_row=2 if newrow>2 else None
   if template_row:
    for col in range(1,dst.max_column+1):
     tmpl=dst.cell(template_row,col); cell=dst.cell(newrow,col)
     if tmpl.has_style: cell._style=copy(tmpl._style)
     if tmpl.number_format: cell.number_format=tmpl.number_format
   for col in range(1,dst.max_column+1): dst.cell(newrow,col).alignment=Alignment(vertical="top",wrap_text=True)
  dst.auto_filter.ref=dst.dimensions; dst.freeze_panes="A2"; dst.column_dimensions["A"].width=32
 # SUS bukan bagian evaluasi: buang sheet SUS lama dari workbook kumulatif bila ada.
 for name in REMOVED_SHEETS:
  if name in existing.sheetnames: del existing[name]
 # Replace current summary with this run while retaining prior summaries in Riwayat Run.
 old_summary=existing["Ringkasan"]
 idx=existing.sheetnames.index("Ringkasan")
 existing.remove(old_summary)
 latest=existing.create_sheet("Ringkasan",idx)
 copy_sheet(current["Ringkasan"],latest)
 existing.calculation.fullCalcOnLoad=True; existing.calculation.forceFullCalc=True
 temp=output.with_name(output.stem+".append_tmp"+output.suffix)
 existing.save(temp)
 existing.close()
 shutil.copyfile(temp,output)
 temp.unlink(missing_ok=True)

def main():
 p=argparse.ArgumentParser(description=__doc__); p.add_argument("--results",required=True); p.add_argument("--output",required=True); p.add_argument("--append",action="store_true",help="Tambahkan sesi ini ke workbook yang sudah ada."); p.add_argument("--replace-existing-ids",action="store_true",help="Ganti baris detail untuk Question ID yang muncul dalam sesi baru; sesi lama tetap di Riwayat Run."); a=p.parse_args()
 rp=Path(a.results); out=Path(a.output); evaluation=json.loads(rp.read_text(encoding="utf-8")); records=rows_from(evaluation)
 wb=Workbook(); summary=wb.active; summary.title="Ringkasan"
 summary.sheet_view.showGridLines=False; summary.merge_cells("A1:F1"); summary["A1"]="Evaluasi Vector RAG vs Graph RAG"; summary["A1"].font=Font(size=16,bold=True,color=WHITE); summary["A1"].fill=PatternFill("solid",fgColor=NAVY); summary["A1"].alignment=Alignment(vertical="center"); summary.row_dimensions[1].height=30
 meta=[("Waktu run",evaluation.get("created_at") or evaluation.get("finished_at")),("Golden set",evaluation.get("golden_set")),("Top-k",evaluation.get("top_k")),("Corpus",evaluation.get("corpus")),("Pertanyaan dijalankan",evaluation.get("golden_questions_run",evaluation.get("questions",len({r.get('id') for r in records})))),("Target request",evaluation.get("planned_cases",evaluation.get("planned_rag_requests",len(records)))),("Request tercatat",evaluation.get("completed_cases",evaluation.get("saved_requests",len(records)))),("Request gagal",evaluation.get("failed_cases",evaluation.get("failed_requests",sum(error_for(r) for r in records)))),("Belum dijalankan",evaluation.get("not_run_cases",evaluation.get("not_run_requests",0))), ("Catatan",evaluation.get("preflight_error") or evaluation.get("aborted_reason") or "Tidak ada benchmark baru yang dibuat saat ekspor ini.")]
 for i,(k,v) in enumerate(meta,3): summary.cell(i,1,k).font=Font(bold=True,color=NAVY); summary.cell(i,2,txt(v)); summary.cell(i,1).fill=PatternFill("solid",fgColor=BLUE)
 summary.cell(15,1,"Ringkasan per metode"); summary.cell(15,1).font=Font(bold=True,size=12,color=NAVY)
 headers=["Metode","Request dicoba","HTTP/API berhasil","Success rate","Generation berhasil","Rata-rata latency (ms)"]
 for j,h in enumerate(headers,1):
  c=summary.cell(16,j,h); c.fill=PatternFill("solid",fgColor=NAVY); c.font=Font(color=WHITE,bold=True); c.alignment=Alignment(wrap_text=True,vertical="center")
 methods=[("vector","Vector RAG"),("graph","Graph RAG")]
 for ri,(mode,label) in enumerate(methods,17):
  rs=[r for r in records if r.get("mode")==mode]; api_ok=sum(bool(r.get("success")) for r in rs); generated=sum((r.get("generation") or {}).get("status")=="generated" or r.get("answer_mode")=="llm" for r in rs)
  vals=[label,len(rs),api_ok,api_ok/len(rs) if rs else None,generated,average([r.get("client_latency_ms",r.get("server_latency_ms")) for r in rs])]
  for j,v in enumerate(vals,1): summary.cell(ri,j,v)
  summary.cell(ri,4).number_format="0.0%"; summary.cell(ri,6).number_format="#,##0.00"
 for col,w in {"A":34,"B":72,"C":24,"D":18,"E":25,"F":28}.items():summary.column_dimensions[col].width=w
 summary.freeze_panes="A16"

 # Main metric matrix retains the user's thirteen metrics and leaves unsupported/manual scores empty.
 matrix=[]
 for dim,name,purpose,key in METRICS:
  vals=[]
  for mode,_ in methods:
   rs=[r for r in records if r.get("mode")==mode]
   if key in {"precision","recall","mrr","hit"}:
    vals.append(average([metric_values(r)[key] for r in rs]))
   elif key in {"faithfulness","correctness","answer_relevancy"}:
    field={"faithfulness":"faithfulness_score","correctness":"answer_correctness_score","answer_relevancy":"answer_relevancy_score"}[key]
    vals.append(average([judge_of(r).get(field) for r in rs]))
   elif key=="latency": vals.append(average([r.get("client_latency_ms",r.get("server_latency_ms")) for r in rs]))
   elif key=="availability":
    attempted=len(rs); vals.append(sum(bool(r.get("success")) for r in rs)/attempted if attempted else None)
   else: vals.append(None)
  stat={"precision":"Otomatis; relevansi dokumen dari expected_source_files","recall":"Otomatis; dokumen unik dari expected_source_files","mrr":"Otomatis; rank chunk pertama dari expected_source_files","hit":"Otomatis","faithfulness":"Belum dinilai; tidak ada nilai judge pada laporan ini" if not any(judge_of(r).get("faithfulness_score") is not None for r in records) else "LLM-as-a-Judge; verifikasi manual disarankan","correctness":"Belum dinilai; tidak ada nilai judge pada laporan ini" if not any(judge_of(r).get("answer_correctness_score") is not None for r in records) else "LLM-as-a-Judge; verifikasi manual disarankan","citation_precision":"Perlu penilaian dukungan sitasi terhadap klaim","citation_coverage":"Perlu hitung klaim dan sitasi pendukung","answer_relevancy":"Belum dinilai; tidak ada nilai judge pada laporan ini" if not any(judge_of(r).get("answer_relevancy_score") is not None for r in records) else "LLM-as-a-Judge; verifikasi manual disarankan","latency":"Rata-rata latency klien dalam milidetik","availability":"HTTP/API success rate; kualitas jawaban dipisah","traceability":"Jejak request tersedia pada sheet Permintaan, Retrieval Detail, Konteks LLM, dan Trace","sus":"Belum ada respons responden"}[key]
  matrix.append([dim,name,purpose,vals[0],vals[1],stat])
 ws=add_table_sheet(wb,"Matriks Metrik",["Dimensi","Metrik","Tujuan","Vector RAG","Graph RAG","Status / cara baca"],matrix,{"A":18,"B":34,"C":78,"D":18,"E":18,"F":52})
 for row in range(2,ws.max_row+1):
  for col in (4,5):
   ws.cell(row,col).number_format="0.00"
  if ws.cell(row,2).value in ("Availability / Success Rate",):
   for col in (4,5):ws.cell(row,col).number_format="0.0%"
  if ws.cell(row,2).value=="Latency":
   for col in (4,5):ws.cell(row,col).number_format="#,##0.00"

 request_rows=[]; retrieval_rows=[]; context_rows=[]; trace_rows=[]; err_rows=[]; review_rows=[]
 for r in records:
  mode="Vector RAG" if r.get("mode")=="vector" else "Graph RAG" if r.get("mode")=="graph" else r.get("mode")
  gen=r.get("generation") or {}; citations=r.get("citations") or r.get("used_citations") or []; validation=r.get("validation") or {}; judge=judge_of(r)
  request_rows.append([r.get("id"),r.get("document_id"),mode,r.get("question"),r.get("expected_answer"),", ".join(r.get("expected_source_files") or []),r.get("success"),r.get("eval_status"),r.get("answer_mode"),r.get("answer"),json.dumps(citations,ensure_ascii=False,default=str),r.get("source_ids_in_answer"),r.get("citation_ids_structurally_valid"),r.get("client_latency_ms",r.get("server_latency_ms")),r.get("server_latency_ms"),gen.get("status"),gen.get("model"),gen.get("error_message") or r.get("error"),judge.get("faithfulness_score"),judge.get("faithfulness_reason"),judge.get("answer_correctness_score"),judge.get("answer_correctness_reason"),judge.get("answer_relevancy_score"),judge.get("answer_relevancy_reason"),r.get("evaluation_run_id")])
  expected={basename(s) for s in r.get("expected_source_files") or []}
  candidates=r.get("retrieved_candidates") or (r.get("retrieval") or {}).get("candidate_chunks") or []
  for rank,c in enumerate(candidates,1):
   fname=c.get("file_name") or c.get("source_file")
   retrieval_rows.append([r.get("id"),mode,rank,c.get("chunk_id"),c.get("doc_id"),fname,c.get("score"),bool(fname and basename(fname) in expected),json.dumps(c.get("retrieval_methods") or [],ensure_ascii=False),c.get("snippet") or c.get("text")])
  ctx=r.get("llm_context")
  if not isinstance(ctx,list):
   ctx=r.get("context_sent_to_llm")
  if isinstance(ctx,list):
   for rank,c in enumerate(ctx,1): context_rows.append([r.get("id"),mode,c.get("n",rank),c.get("chunk_id"),c.get("doc_id"),c.get("file_name"),c.get("title"),c.get("section"),json.dumps(c.get("retrieval_methods") or [],ensure_ascii=False),(c.get("text") or "")+"".join(f"\n({'percakapan sebelumnya' if nb.get('position')=='before' else 'percakapan berikutnya'}, chunk {nb.get('chunk_id')}) {nb.get('text') or ''}" for nb in (c.get("neighbors") or []))])
  elif ctx: context_rows.append([r.get("id"),mode,1,None,None,None,None,None,None,ctx])
  trace=r.get("retrieval_trace") or (r.get("retrieval") or {}).get("retrieval_trace") or []
  if isinstance(trace,list):
   for seq,item in enumerate(trace,1): trace_rows.append([r.get("id"),mode,seq,json.dumps(item,ensure_ascii=False,default=str)])
  if error_for(r): err_rows.append([r.get("id"),mode,r.get("http_status"),r.get("eval_status"),gen.get("status"),r.get("error") or gen.get("error_message"),r.get("client_latency_ms",r.get("server_latency_ms")),r.get("evaluation_run_id")])
  if not judge or judge.get("status")!="scored":
   for metric in ("Faithfulness","Answer Correctness","Answer Relevancy"):
    review_rows.append([r.get("id"),mode,metric,"",judge.get("status") or "Belum dijalankan","Nilai dan alasan hanya diisi setelah penilaian berbasis konteks aktual.",r.get("evaluation_run_id")])
  for metric,definition in (("Citation Precision","Periksa setiap sitasi apakah mendukung klaim yang dilekatinya."),("Citation Coverage","Hitung klaim faktual dan klaim yang disertai sitasi pendukung.")):
   review_rows.append([r.get("id"),mode,metric,"","Perlu review manual",definition,r.get("evaluation_run_id")])
  if r.get("eval_status") not in ("ANSWERED","PARTIAL") or not r.get("success"):
   review_rows.append([r.get("id"),mode,"Kesesuaian jawaban","","Perlu review manual","Tinjau status, pertanyaan, jawaban acuan, jawaban aktual, serta konteks pada sheet terkait.",r.get("evaluation_run_id")])

 add_table_sheet(wb,"Permintaan",["Question ID","Document ID","Metode","Pertanyaan","Jawaban acuan","Expected source files","API berhasil","Status evaluasi","Answer mode","Jawaban","Sitasi (JSON)","Nomor sitasi di jawaban","Struktur sitasi valid","Latency klien (ms)","Latency server (ms)","Status generation","Model","Error generation/request","Faithfulness","Alasan Faithfulness","Answer Correctness","Alasan Correctness","Answer Relevancy","Alasan Relevancy","Run ID"],request_rows,{"A":18,"B":15,"C":16,"D":60,"E":60,"F":48,"G":14,"H":22,"I":16,"J":64,"K":52,"L":22,"M":22,"N":18,"O":18,"P":20,"Q":24,"R":45,"S":16,"T":50,"U":20,"V":50,"W":18,"X":50,"Y":40})
 add_table_sheet(wb,"Retrieval Detail",["Question ID","Metode","Rank","Chunk ID","Document ID","File sumber","Score retrieval","Sumber diharapkan","Metode retrieval","Snippet / isi chunk"],retrieval_rows,{"A":18,"B":16,"C":10,"D":32,"E":20,"F":56,"G":18,"H":20,"I":30,"J":80})
 add_table_sheet(wb,"Konteks LLM",["Question ID","Metode","Urutan konteks","Chunk ID","Document ID","File sumber","Judul","Section","Metode retrieval","Teks konteks aktual dikirim ke LLM"],context_rows,{"A":18,"B":16,"C":16,"D":32,"E":20,"F":56,"G":42,"H":34,"I":30,"J":100})
 add_table_sheet(wb,"Trace",["Question ID","Metode","Urutan trace","Detail trace (JSON)"],trace_rows,{"A":18,"B":16,"C":14,"D":110})
 add_table_sheet(wb,"Log Error",["Question ID","Metode","HTTP status","Status evaluasi","Status generation","Error","Latency (ms)","Run ID"],err_rows,{"A":18,"B":16,"C":14,"D":22,"E":22,"F":80,"G":18,"H":40})
 add_table_sheet(wb,"Review Manual",["Question ID","Metode","Metrik / item review","Nilai manual","Status","Panduan review","Run ID"],review_rows,{"A":18,"B":16,"C":30,"D":18,"E":24,"F":86,"G":40})
 cfg=[]
 for k,v in evaluation.items():
  if k=="results": continue
  cfg.append([k,txt(v)])
 add_table_sheet(wb,"Konfigurasi",["Properti run","Nilai"],cfg,{"A":36,"B":110})

 # Apply numeric presentation formats without inventing scores.
 for wsname in ("Permintaan",):
  ws=wb[wsname]
  for row in range(2,ws.max_row+1):
   for col in (14,15): ws.cell(row,col).number_format="#,##0.00"
 for row in range(2,wb["Matriks Metrik"].max_row+1):
  name=wb["Matriks Metrik"].cell(row,2).value
  for col in (4,5):
   if name=="Availability / Success Rate": wb["Matriks Metrik"].cell(row,col).number_format="0.0%"
   elif name=="Latency": wb["Matriks Metrik"].cell(row,col).number_format="#,##0.00"
   else: wb["Matriks Metrik"].cell(row,col).number_format="0.00"
 wb.calculation.fullCalcOnLoad=True; wb.calculation.forceFullCalc=True
 out.parent.mkdir(parents=True,exist_ok=True)
 session=str(evaluation.get("session_id") or rp.stem)
 if a.replace_existing_ids and not a.append:
  p.error("--replace-existing-ids harus digunakan bersama --append")
 if out.exists() and not a.append:
  raise FileExistsError(f"Workbook sudah ada: {out}. Gunakan --append untuk mempertahankan data lama.")
 if a.append and out.exists():
  existing=load_workbook(out)
  append_session(existing,wb,out,session,evaluation,a.replace_existing_ids)
 elif a.append:
  initialize_cumulative(wb,session)
  wb.save(out)
 else:
  wb.save(out)
 # Read-back integrity checks: all metrics and expected data tabs must survive export.
 check=load_workbook(out,read_only=True,data_only=False)
 expected={"Ringkasan","Matriks Metrik","Permintaan","Retrieval Detail","Konteks LLM","Trace","Log Error","Review Manual","Konfigurasi"}
 if not expected.issubset(set(check.sheetnames)): raise RuntimeError("Sheet workbook hilang saat read-back")
 metric_col=3 if a.append and out.exists() and check["Matriks Metrik"].cell(1,1).value=="Session ID" else 2
 metric_names=[check["Matriks Metrik"].cell(row,metric_col).value for row in range(2,check["Matriks Metrik"].max_row+1)]
 if metric_names[-len(METRICS):]!=[x[1] for x in METRICS]: raise RuntimeError("Daftar metrik tidak utuh pada workbook")
 if check["Permintaan"].max_row < len(records)+1: raise RuntimeError("Baris request hasil ekspor tidak lengkap")
 print(json.dumps({"workbook":str(out),"sheets":check.sheetnames,"request_rows_in_this_session":len(records),"total_request_rows":check["Permintaan"].max_row-1,"metric_rows_in_this_session":len(METRICS)},ensure_ascii=False))
if __name__=="__main__": main()
