import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

function argsOf(argv) {
  const out = {};
  for (let i=2; i<argv.length; i++) {
    if (!argv[i].startsWith('--') || !argv[i+1]) throw new Error(`Argumen tidak valid: ${argv[i]}`);
    out[argv[i].slice(2)] = argv[++i];
  }
  for (const key of ['template','results','output']) if (!out[key]) throw new Error(`--${key} wajib diisi`);
  return out;
}

const cli = argsOf(process.argv);
const runtimeHome = process.env.USERPROFILE || os.homedir();
const artifactModule = process.env.ARTIFACT_TOOL_MODULE || path.join(
  runtimeHome, '.cache', 'codex-runtimes', 'codex-primary-runtime', 'dependencies',
  'node', 'node_modules', '@oai', 'artifact-tool', 'dist', 'artifact_tool.mjs'
);
const { FileBlob, SpreadsheetFile } = await import(pathToFileURL(artifactModule).href);
console.log('Artifact Tool dimuat.');
const evaluation = JSON.parse(await fs.readFile(cli.results, 'utf8'));
console.log(`Hasil JSON dibaca: ${(evaluation.results || []).length} request.`);
const resultMap = new Map((evaluation.results || []).map(r => [`${r.id}\0${r.mode}`, r]));
const templateBlob = await FileBlob.load(cli.template);
console.log('File template dimuat.');
const wb = await SpreadsheetFile.importXlsx(templateBlob);
console.log('Template workbook diimpor.');
const answers = wb.worksheets.getItem('Evaluasi Jawaban');
const details = wb.worksheets.getItem('Retrieval Detail');
const recall = wb.worksheets.getItem('Recall Sumber');
const summary = wb.worksheets.getItem('Ringkasan');
const guide = wb.worksheets.getItem('Panduan');

const answerRows = answers.getRange('A5:Y154').values;
const oldDetailRows = details.getRange('A5:L754').values;
const detailRowMap = new Map();
for (let i=0; i<oldDetailRows.length; i++) {
  const row=oldDetailRows[i];
  detailRowMap.set(`${row[0]}\0${row[1]}\0${row[2]}`, {row:i+5, chunkId:row[3], manual:row[9]});
}
const rowByPair = new Map();
for (let i=0; i<answerRows.length; i++) rowByPair.set(`${answerRows[i][0]}\0${answerRows[i][6]}`, i+5);

const answerWrite = {H:[],I:[],J:[],K:[],L:[],M:[],R:[],S:[],T:[],U:[],W:[],X:[],Y:[],Z:[],AA:[]};
for (let i=0; i<answerRows.length; i++) {
  const row=answerRows[i], id=row[0], method=row[6];
  const mode=method==='Vector RAG'?'vector':method==='Graph RAG'?'graph':null;
  const result=mode ? resultMap.get(`${id}\0${mode}`) : null;
  if (!result) {
    for (const [col,values] of Object.entries(answerWrite)) values.push(col==='Z'?'Belum dijalankan':null);
    continue;
  }
  if (!result.success) {
    const note=[row[24], `Run baru gagal; data H:Y dipertahankan dari workbook sumber dan bukan hasil run ini. ${result.error||''}`].filter(Boolean).join(' ');
    const keep={H:row[7],I:row[8],J:row[9],K:row[10],L:row[11],M:row[12],R:row[17],S:row[18],T:row[19],U:row[20],W:row[22],X:row[23],Y:note,Z:'Gagal',AA:''};
    for (const [col,values] of Object.entries(answerWrite)) values.push(keep[col]??null);
    continue;
  }
  const valid=result.citation_ids_structurally_valid;
  let failure='Belum dinilai';
  if (!result.success) failure='Kegagalan lainnya';
  else if (result.answer_mode!=='llm') failure='LLM nonaktif/gagal';
  else if (!result.retrieved_candidates?.length) failure='Dokumen expected tidak ditemukan';
  else {
    const expected=new Set((result.expected_source_files||[]).map(x=>path.basename(String(x).replaceAll('\\','/')).toLocaleLowerCase()));
    const found=(result.retrieved_candidates||[]).some(c=>expected.has(path.basename(String(c.file_name||'').replaceAll('\\','/')).toLocaleLowerCase()));
    if (!found) failure='Dokumen expected tidak ditemukan';
    else if (!result.source_ids_in_answer?.length) failure='Output LLM gagal validasi';
  }
  const notes=[];
  if (!result.context_available_from_api) notes.push('API tidak mengembalikan debug.context_sent_to_llm; konteks aktual tidak dapat diverifikasi.');
  if (result.llm_generation_attempted===false) notes.push('LLM tidak dipanggil pada run ini.');
  if (result.answer_mode!=='llm') notes.push(`answer_mode=${result.answer_mode||'tidak tersedia'}; nilai manual belum diisi.`);
  if (result.error) notes.push(result.error);
  notes.push('Penilaian klaim, dukungan semantik, faithfulness, correctness, dan citation precision memerlukan peninjauan manual.');
  const latency=(result.client_latency_ms ?? result.server_latency_ms);
  const contextText=result.context_available_from_api===false
    ? 'API tidak mengembalikan konteks yang benar-benar dikirim ke LLM.'
    : (result.context_sent_to_llm || 'Tidak ada konteks yang dikirim ke LLM pada run ini.');
  const unchanged=row[7]===contextText && row[8]===(result.answer ?? '');
  answerWrite.H.push(contextText);
  answerWrite.I.push(result.answer ?? '');
  answerWrite.J.push((result.source_ids_in_answer||[]).join(', '));
  answerWrite.K.push(unchanged?row[10]:null);
  answerWrite.L.push(unchanged?row[11]:null);
  answerWrite.M.push(valid===true?'Ya':valid===false?'Tidak':'Belum dinilai');
  answerWrite.R.push(unchanged?row[17]:null);
  answerWrite.S.push(unchanged?row[18]:null);
  answerWrite.T.push(unchanged?row[19]:null);
  answerWrite.U.push(unchanged?row[20]:null);
  answerWrite.W.push(Number.isFinite(latency)?Number((latency/1000).toFixed(3)):null);
  answerWrite.X.push(failure);
  answerWrite.Y.push(notes.join(' '));
  answerWrite.Z.push(result.run_status || (result.success?'Selesai':'Gagal'));
  answerWrite.AA.push(result.evaluation_run_id || '');
}
for (const [col, values] of Object.entries(answerWrite)) {
  if (col==='Z') {
    answers.getRange('Z4').values=[['Status Run (Selesai/Gagal/Belum dijalankan)']];
    answers.getRange(`Z5:Z154`).values=values.map(v=>[v]);
  } else if (col==='AA') {
    answers.getRange('AA4').values=[['Evaluation Run ID API']];
    answers.getRange(`AA5:AA154`).values=values.map(v=>[v]);
  } else answers.getRange(`${col}5:${col}154`).values=values.map(v=>[v]);
}

// Keep a reviewer judgement only when the same chunk remains at the same rank.
const detailColumnIndex={D:3,E:4,F:5,G:6,J:9,K:10,L:11};
const candidateCells=Object.fromEntries(Object.entries(detailColumnIndex).map(([col,index])=>[
  col,oldDetailRows.map(row=>col==='J' && row[11]!=='Ya' ? null : (row[index]??null))
]));
for (const [pair, answerRow] of rowByPair.entries()) {
  const [id, method] = pair.split('\0');
  const mode=method==='Vector RAG'?'vector':'graph';
  const result=resultMap.get(`${id}\0${mode}`);
  if (!result?.success) continue;
  const candidates=(result.retrieved_candidates||[]).slice(0,5);
  for (let rank=1; rank<=5; rank++) {
    const key=`${id}\0${method}\0${rank}`;
    const detail=detailRowMap.get(key);
    if (!detail) continue;
    const offset=detail.row-5;
    const c=candidates.find(x=>Number(x.rank||0)===rank) || candidates[rank-1];
    if (!c) {
      for (const col of Object.keys(candidateCells)) candidateCells[col][offset]=null;
      continue;
    }
    const chunkId=c.chunk_id||'';
    const prior=detail.chunkId===chunkId && ['Ya','Tidak','Belum dinilai'].includes(detail.manual) ? detail.manual : 'Belum dinilai';
    const snippet=c.snippet||'';
    const evidenceNote=[snippet,`Metode retrieval: ${(c.retrieval_methods||[]).join(', ')||'tidak dicatat'}`].filter(Boolean).join('\n');
    candidateCells.D[offset]=chunkId; candidateCells.E[offset]=c.doc_id||'';
    candidateCells.F[offset]=c.file_name||''; candidateCells.G[offset]=Number.isFinite(c.score)?c.score:null;
    candidateCells.J[offset]=prior; candidateCells.K[offset]=evidenceNote;
    candidateCells.L[offset]='Ya';
  }
}
for (const [col, cells] of Object.entries(candidateCells)) {
  details.getRange(`${col}5:${col}754`).values=cells.map(value=>[value]);
}

// Formula H remains the template's expected-filename comparison; refresh it for every slot.
details.getRange('H5:H754').formulas=Array.from({length:750},(_,i)=>{
  const r=i+5;
  return [[`=IF(OR(F${r}="",L${r}<>"Ya"),"",IF(ISNUMBER(SEARCH(F${r},I${r})),"Ya","Tidak"))`]];
});

const rowCount=answerRows.length;
const answerFormulas={N:[],O:[],P:[],Q:[],V:[]};
for (let r=5; r<5+rowCount; r++) {
  const run=`'Evaluasi Jawaban'!$Z$5:$Z$154`;
  const id=`'Retrieval Detail'!$A$5:$A$754`;
  const method=`'Retrieval Detail'!$B$5:$B$754`;
  const recorded=`'Retrieval Detail'!$L$5:$L$754`;
  const match=`'Retrieval Detail'!$H$5:$H$754`;
  const support=`'Retrieval Detail'!$J$5:$J$754`;
  const unresolved=`COUNTIFS(${id},A${r},${method},G${r},${recorded},"Ya",${support},"<>Ya",${support},"<>Tidak")>0`;
  const done=`COUNTIFS('Evaluasi Jawaban'!$A$5:$A$154,A${r},'Evaluasi Jawaban'!$G$5:$G$154,G${r},${run},"Selesai")>0`;
  answerFormulas.N.push([`=IF(NOT(${done}),"",IF(${unresolved},"",IF(COUNTIFS(${id},A${r},${method},G${r},${recorded},"Ya")=0,"",COUNTIFS(${id},A${r},${method},G${r},${recorded},"Ya",${match},"Ya",${support},"Ya")/COUNTIFS(${id},A${r},${method},G${r},${recorded},"Ya"))))`]);
  answerFormulas.O.push([`=IF(NOT(${done}),"",IF(${unresolved},"",IF(COUNTIFS('Recall Sumber'!$A$5:$A$154,A${r},'Recall Sumber'!$B$5:$B$154,G${r})=0,"",COUNTIFS('Recall Sumber'!$A$5:$A$154,A${r},'Recall Sumber'!$B$5:$B$154,G${r},'Recall Sumber'!$D$5:$D$154,"Ya")/COUNTIFS('Recall Sumber'!$A$5:$A$154,A${r},'Recall Sumber'!$B$5:$B$154,G${r}))))`]);
  const rrParts=[];
  for (let rank=5; rank>=1; rank--) rrParts.unshift(`IF(COUNTIFS(${id},A${r},${method},G${r},'Retrieval Detail'!$C$5:$C$754,${rank},${match},"Ya",${support},"Ya",${recorded},"Ya")>0,${(1/rank).toFixed(6)},`);
  answerFormulas.P.push([`=IF(NOT(${done}),"",IF(${unresolved},"",${rrParts.join('')}0${')'.repeat(5)}))`]);
  answerFormulas.Q.push([`=IF(NOT(${done}),"",IF(${unresolved},"",IF(COUNTIFS(${id},A${r},${method},G${r},${match},"Ya",${support},"Ya",${recorded},"Ya")>0,1,0)))`]);
  answerFormulas.V.push([`=IF(OR(Z${r}<>"Selesai",K${r}="",K${r}=0,L${r}="",L${r}>K${r}),"",L${r}/K${r})`]);
}
for (const [col, formulas] of Object.entries(answerFormulas)) answers.getRange(`${col}5:${col}154`).formulas=formulas;

const recallRows=recall.getRange('A5:C154').values;
const recallFormulas=[];
for (let i=0; i<recallRows.length; i++) {
  const r=i+5;
  recallFormulas.push([`=IF(COUNTIFS('Evaluasi Jawaban'!$A$5:$A$154,A${r},'Evaluasi Jawaban'!$G$5:$G$154,B${r},'Evaluasi Jawaban'!$Z$5:$Z$154,"Selesai")=0,"",IF(COUNTIFS('Retrieval Detail'!$A$5:$A$754,A${r},'Retrieval Detail'!$B$5:$B$754,B${r},'Retrieval Detail'!$L$5:$L$754,"Ya",'Retrieval Detail'!$H$5:$H$754,"Ya",'Retrieval Detail'!$J$5:$J$754,"<>Ya",'Retrieval Detail'!$J$5:$J$754,"<>Tidak")>0,"",IF(COUNTIFS('Retrieval Detail'!$A$5:$A$754,A${r},'Retrieval Detail'!$B$5:$B$754,B${r},'Retrieval Detail'!$F$5:$F$754,C${r},'Retrieval Detail'!$C$5:$C$754,"<=5",'Retrieval Detail'!$H$5:$H$754,"Ya",'Retrieval Detail'!$J$5:$J$754,"Ya",'Retrieval Detail'!$L$5:$L$754,"Ya")>0,"Ya","Tidak")))`]);
}
recall.getRange('D5:D154').formulas=recallFormulas;

// Summary averages only completed runs; all answer-quality scores remain empty until reviewed.
for (let r=6; r<=15; r++) {
  const srcCol=r===6?'N':r===7?'O':r===8?'P':r===9?'Q':r===10?'R':r===11?'S':r===13?'U':r===14?'V':'W';
  if (r===12) {
    summary.getRange('B12').formulas=[[`=IFERROR(COUNTIFS('Evaluasi Jawaban'!$G$5:$G$154,"Vector RAG",'Evaluasi Jawaban'!$M$5:$M$154,"Ya")/(COUNTIFS('Evaluasi Jawaban'!$G$5:$G$154,"Vector RAG",'Evaluasi Jawaban'!$M$5:$M$154,"Ya")+COUNTIFS('Evaluasi Jawaban'!$G$5:$G$154,"Vector RAG",'Evaluasi Jawaban'!$M$5:$M$154,"Tidak")),"")`]];
    summary.getRange('C12').formulas=[[`=IFERROR(COUNTIFS('Evaluasi Jawaban'!$G$5:$G$154,"Graph RAG",'Evaluasi Jawaban'!$M$5:$M$154,"Ya")/(COUNTIFS('Evaluasi Jawaban'!$G$5:$G$154,"Graph RAG",'Evaluasi Jawaban'!$M$5:$M$154,"Ya")+COUNTIFS('Evaluasi Jawaban'!$G$5:$G$154,"Graph RAG",'Evaluasi Jawaban'!$M$5:$M$154,"Tidak")),"")`]];
  } else {
    for (const [col,method] of [['B','Vector RAG'],['C','Graph RAG']]) {
      summary.getRange(`${col}${r}`).formulas=[[`=IF(COUNTIFS('Evaluasi Jawaban'!$G$5:$G$154,"${method}",'Evaluasi Jawaban'!$Z$5:$Z$154,"Selesai")=0,"",IFERROR(AVERAGEIFS('Evaluasi Jawaban'!$${srcCol}$5:$${srcCol}$154,'Evaluasi Jawaban'!$G$5:$G$154,"${method}",'Evaluasi Jawaban'!$Z$5:$Z$154,"Selesai"),""))`]];
    }
  }
}
summary.getRange('A16:E17').values=[
  ['Run selesai','','','','Jumlah pertanyaan-metode yang API-nya berhasil menyelesaikan request.'],
  ['Run gagal','','','','Request gagal/timeout; hasil dan metriknya tidak dianggap nol.'],
];
for (const [col,method] of [['B','Vector RAG'],['C','Graph RAG']]) {
  summary.getRange(`${col}16`).formulas=[[`=COUNTIFS('Evaluasi Jawaban'!$G$5:$G$154,"${method}",'Evaluasi Jawaban'!$Z$5:$Z$154,"Selesai")`]];
  summary.getRange(`${col}17`).formulas=[[`=COUNTIFS('Evaluasi Jawaban'!$G$5:$G$154,"${method}",'Evaluasi Jawaban'!$Z$5:$Z$154,"Gagal")`]];
}
summary.getRange('D16:D17').values=[[''],['']];

guide.getRange('B14').values=[['Jumlah kandidat Top-5 dari file expected yang juga ditandai manual relevan (Retrieval Detail J=Ya) ÷ jumlah kandidat aktual yang direkam. Nilai kosong sampai semua kandidat dinilai.']];
guide.getRange('C14').values=[['Chunk dari dokumen benar belum otomatis relevan; reviewer harus memeriksa isi setiap kandidat.']];
guide.getRange('B15').values=[['Jumlah file expected unik yang memiliki sedikitnya satu chunk Top-5 yang cocok dan dinilai relevan (H=Ya, J=Ya) ÷ seluruh file expected unik. Kosong sampai kandidat expected dinilai.']];
guide.getRange('B16').values=[['Reciprocal rank dari kemunculan pertama chunk Top-5 yang cocok dengan file expected dan dinilai relevan; 0 jika run selesai dan tidak ada yang relevan.']];
guide.getRange('C16').values=[['Rank dari hasil retrieval API, bukan urutan sitasi atau panel UI.']];
guide.getRange('B17').values=[['1 jika run selesai dan setidaknya satu chunk Top-5 dari file expected dinilai relevan; 0 jika tidak ada; kosong jika belum dinilai.']];
guide.getRange('B18').values=[['Metrik yang bergantung pada relevansi chunk menunggu kolom J diisi Ya/Tidak. Status run dan skor kosong mencegah data yang belum dijalankan dihitung sebagai nol.']];
guide.getRange('A24:B24').values=[['Status run dan ID API','Evaluasi Jawaban kolom Z menunjukkan Selesai/Gagal/Belum dijalankan. Kolom AA menyimpan evaluation_run_id API untuk melacak request.']];
summary.getRange('E6').values=[['Kandidat Top-5 yang cocok dengan file expected dan dinilai relevan ÷ seluruh kandidat aktual; kosong sampai tinjauan relevansi selesai.']];
summary.getRange('E7').values=[['File expected unik yang ditemukan melalui chunk yang dinilai relevan ÷ seluruh file expected unik.']];
summary.getRange('E8').values=[['Reciprocal rank kemunculan pertama chunk expected yang dinilai relevan; 0 jika run selesai tanpa hasil relevan.']];
summary.getRange('E9').values=[['Proporsi run selesai yang memiliki setidaknya satu chunk expected yang dinilai relevan.']];

answers.getRange('Z4:AA4').format.fill='#D9EAF7';
answers.getRange('Z4:AA154').format.wrapText=true;
answers.getRange('Z4:Z154').format.columnWidth=30;
answers.getRange('AA4:AA154').format.columnWidth=38;
console.log('Data dan formula workbook diperbarui. Menghitung ulang...');
wb.recalculate();
console.log('Perhitungan selesai. Menyimpan workbook...');
await (await SpreadsheetFile.exportXlsx(wb)).save(cli.output);
console.log(JSON.stringify({output:cli.output, successfulRuns:evaluation.completed_cases, failedRuns:evaluation.failed_cases,
  manualReviewRequired:150, sheets:wb.worksheets.items.map(s=>s.name)}));
