import {request,normalizeUrl,validateSettings,progressText,friendlyError} from './shared.js';
const $=id=>document.getElementById(id);let info=null,infoUrl='',snapshot=null,ready=false,busy=false;
if(new URLSearchParams(location.search).has('full'))document.body.classList.add('full');
const say=(text,error=false)=>{$('message').textContent=text;$('message').classList.toggle('error',error);$('message').hidden=false;};
function tab(name){document.querySelectorAll('[data-tab]').forEach(b=>b.classList.toggle('selected',b.dataset.tab===name));$('download-panel').hidden=name!=='download';$('queue-panel').hidden=name!=='queue';}
document.querySelectorAll('[data-tab]').forEach(b=>b.onclick=()=>tab(b.dataset.tab));
$('settings').onclick=()=>chrome.runtime.openOptionsPage();
$('expand').onclick=()=>chrome.tabs.create({url:chrome.runtime.getURL('popup.html?full=1')});
$('extension-id').textContent=chrome.runtime.id;
$('copy-id').onclick=async()=>{try{await navigator.clipboard.writeText(chrome.runtime.id);say('Өргөтгөлийн ID хуулагдлаа.');}catch{say('ID-г сонгоод Ctrl+C дарж хуулна уу.');}};
async function current(){
 const [t]=await chrome.tabs.query({active:true,currentWindow:true});
 if(t?.url&&/^https?:/.test(t.url))$('url').value=t.url;
 else say('Видео байгаа табаас өргөтгөлийг нээнэ үү. Эсвэл холбоосоо оруулна уу.');
 resetInfo();
}
$('current').onclick=current;
function resetInfo(){info=null;infoUrl='';$('preview').hidden=true;$('playlist').hidden=true;}
$('url').oninput=resetInfo;
function renderInfo(r){
 $('preview').hidden=!!r.playlist;$('playlist').hidden=!r.playlist;
 if(r.playlist){
  $('playlist-title').textContent=`${r.title} · ${r.count} бичлэг`;
  $('playlist-entries').replaceChildren();
  for(const entry of r.entries){const label=document.createElement('label'),check=document.createElement('input'),text=document.createElement('span');check.type='checkbox';check.value=entry.url;text.textContent=entry.title;label.append(check,text);$('playlist-entries').append(label);}
 }else{
  $('video-title').textContent=r.title;$('video-meta').textContent=[r.site,r.duration?`${Math.floor(r.duration/60)} мин ${Math.floor(r.duration%60)} сек`:null,r.heights?.length?`Дээд ${Math.max(...r.heights)}p`:null].filter(Boolean).join(' · ');
  $('thumbnail').hidden=!r.thumbnail;if(r.thumbnail)$('thumbnail').src=r.thumbnail;
 }
}
async function inspect(){
 const url=normalizeUrl($('url').value);
 const result=await request('inspect',{url});info=result;infoUrl=url;renderInfo(result);return result;
}
function selection(){return validateSettings({format:$('format').value,quality:Number($('quality').value),oneClick:snapshot?.settings.oneClick||false});}
async function add(url,title){const s=selection();await request('settings',s);return request('enqueue',{url,title,...s});}
async function download(){
 const url=normalizeUrl($('url').value);
 if(!info||infoUrl!==url)await inspect();
 if(info.playlist){
  const checks=[...$('playlist-entries').querySelectorAll('input:checked')];
  if(!checks.length){say('Татах бичлэгүүдээ сонгоод дахин «Татах» дарна уу.');return;}
  let count=0,errors=[];
  for(const c of checks){try{await add(c.value,c.nextElementSibling.textContent);count++;}catch(e){errors.push(e.message);}}
  say(`${count} бичлэг нэмэгдлээ.${errors.length?' '+errors.length+' холбоос нэмэгдсэнгүй: '+errors[0]:''}`,!!errors.length);
 }else{await add(url,info.title);say('Таталтын дараалалд нэмэгдлээ.');}
 tab('queue');await refresh();
}
async function run(button,fn){if(busy)return;busy=true;button.disabled=true;const old=button.textContent;button.textContent='Түр хүлээнэ үү…';try{await fn();}catch(e){say(friendlyError(e.message),true);}finally{busy=false;button.disabled=false;button.textContent=old;}}
$('inspect').onclick=()=>run($('inspect'),inspect);
$('download').onclick=()=>run($('download'),download);
$('format').onchange=()=>{$('quality').disabled=$('format').value==='mp3';$('download-hint').textContent=$('format').value==='mp3'?'Аудиог MP3 · 192 kbps болгон хөрвүүлнэ.':'MP4-т тохирох эх сурвалжийн боломжит чанараар татна.';};
$('batch-add').onclick=()=>run($('batch-add'),async()=>{
 const lines=$('batch').value.split(/\r?\n/).map(v=>v.trim()).filter(Boolean);
 if(!lines.length||lines.length>100)throw new Error('1–100 холбоос оруулна уу.');
 const urls=[...new Set(lines.map(normalizeUrl))];let count=0;const errors=[];
 for(const url of urls){try{const r=await request('inspect',{url});if(r.playlist){errors.push('Олон бичлэгтэй холбоосыг үндсэн хэсэгт сонгож нэмнэ үү.');continue;}await add(url,r.title);count++;}catch(e){errors.push(e.message);}}
 say(`${count} бичлэг нэмэгдлээ.${errors.length?' '+errors.length+' холбоос нэмэгдсэнгүй: '+errors[0]:''}`,!!errors.length);tab('queue');await refresh();
});
const labels={queued:'Хүлээж байна',downloading:'Татаж байна',processing:'Нэгтгэж байна',done:'Дууссан',error:'Алдаа',cancelled:'Цуцлагдсан',interrupted:'Тасарсан'};
function renderJobs(jobs){
 $('queue-count').textContent=jobs.filter(j=>['queued','downloading','processing'].includes(j.status)).length;
 $('jobs').replaceChildren();
 if(!jobs.length){const box=document.createElement('div');box.className='empty card';const icon=document.createElement('span');icon.className='empty-icon';icon.textContent='↓';const title=document.createElement('strong');title.textContent='Эхний бичлэгээ татаарай';const p=document.createElement('span');p.textContent='Таталтын явц, хадгалсан бичлэгүүд энд харагдана.';box.append(icon,title,p);$('jobs').append(box);return;}
 for(const j of jobs){
  const card=document.createElement('article');card.className=`job card ${j.status}`;
  const title=document.createElement('div');title.className='job-title';title.textContent=j.title;
  const meta=document.createElement('div');meta.className='job-meta';const format=document.createElement('span'),pc=document.createElement('span');format.textContent=`${j.format.toUpperCase()}${j.format==='mp4'?' · '+j.quality+'p хүртэл':''}`;pc.textContent=progressText(j.progress);meta.append(format,pc);
  const track=document.createElement('div'),bar=document.createElement('div');track.className='progress-track';bar.className='progress-bar';bar.style.width=progressText(j.progress);track.append(bar);
  const foot=document.createElement('div');foot.className='job-footer';const state=document.createElement('span');state.textContent=[labels[j.status]||j.status,j.speed?`${(j.speed/1048576).toFixed(1)} MB/с`:'',j.eta?`${Math.ceil(j.eta)} сек`:''].filter(Boolean).join(' · ');foot.append(state);
  const b=document.createElement('button');b.className='text-btn';
  if(['queued','downloading','processing'].includes(j.status)){b.textContent='Цуцлах';b.onclick=()=>run(b,async()=>{await request('cancel',{id:j.id});await refresh();});}
  else if(j.status==='done'){b.textContent='Хавтас нээх ↗';b.onclick=()=>run(b,()=>request('open_folder',{id:j.id}));}
  else{b.textContent='Дахин татах ↻';b.onclick=()=>run(b,async()=>{await request('enqueue',{url:j.url,title:j.title,folder:j.folder,format:j.format,quality:j.quality});await refresh();});}
  foot.append(b);card.append(title,meta,track,foot);
  if(j.error){const e=document.createElement('div');e.className='job-error';e.textContent=j.error;card.append(e);}
  $('jobs').append(card);
 }
}
async function refresh(){snapshot=await request('snapshot');renderJobs(snapshot.jobs);$('queue-count').textContent=snapshot.active_count??snapshot.jobs.filter(j=>['queued','downloading','processing'].includes(j.status)).length;if(snapshot.omitted){const note=document.createElement('p');note.className='muted';note.textContent=`Хуучин түүх, дарааллын ${snapshot.omitted} бичлэг дэлгэцэд багтаагүй. Таталтууд дарааллаар үргэлжилнэ.`;$('jobs').append(note);}}
$('refresh').onclick=()=>run($('refresh'),refresh);
async function init(){
 try{await current();}catch{}
 try{
  const h=await request('health');ready=h.ready;$('connection').textContent=h.ready?'● Татахад бэлэн':'● Туслах хэрэгсэл дутуу';$('connection').classList.toggle('ready',h.ready);$('setup').hidden=h.ready;
  await refresh();$('format').value=snapshot.settings.format;$('quality').value=snapshot.settings.quality;$('format').onchange();
  if(!h.ready)say(h.message,true);
  if(h.ready&&snapshot.settings.oneClick&&$('url').value)await run($('download'),download);
 }catch(e){$('connection').textContent='● Суулгац шаардлагатай';$('setup').hidden=false;say(friendlyError(e.message),true);renderJobs([]);}
}
setInterval(()=>{if(ready&&!document.hidden)refresh().catch(()=>{});},1800);
init();
