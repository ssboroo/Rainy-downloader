import {resolveVideoUrl,isPlayingVideo} from './video-source.js';
const controls=new Map();let scheduled=false;
const css=`:host{all:initial;font-family:'Segoe UI',Arial,sans-serif}*{box-sizing:border-box}button,select{font:inherit}button{cursor:pointer}.download{border:1px solid #ffffff80;background:linear-gradient(110deg,#3b84ff,#245de5);color:white;box-shadow:0 4px 18px #103f8b45;border-radius:10px;padding:9px 14px;font-size:12px;font-weight:650;white-space:nowrap}.download:hover{background:#1d5be4}.panel{margin-top:7px;width:235px;background:#fff;color:#24385e;padding:16px;border-radius:14px;border:1px solid #dfebff;box-shadow:0 10px 35px #15305835;font-size:12px;line-height:1.6}strong{display:block;margin-bottom:9px}select{width:100%;padding:8px;margin-bottom:8px;border:1px solid #dce7f8;border-radius:7px;background:#f8faff;color:#385278}.go{width:100%;border:0;border-radius:8px;background:#2868f4;color:#fff;padding:9px;font-size:12px;font-weight:600}.go:disabled{opacity:.55;cursor:wait}.note{display:block;font-size:10px;color:#7185a5;margin-top:8px;overflow-wrap:anywhere}button:focus-visible,select:focus-visible{outline:3px solid #99bfff;outline-offset:2px}[hidden]{display:none!important}`;
function rpc(action,payload={}){return new Promise((resolve,reject)=>{chrome.runtime.sendMessage({action,payload},r=>{const e=chrome.runtime.lastError;if(e||!r?.ok)reject(new Error(e?.message||r?.error||'Холболт тасарсан.'));else resolve(r.data);});});}
function source(video){
 const card=video.closest('article,[role="article"],ytd-rich-item-renderer,ytd-reel-video-renderer,ytd-video-renderer');
 const anchors=card?[...card.querySelectorAll('a[href]')].map(a=>a.href):[];
 return resolveVideoUrl({pageUrl:location.href,anchors,mediaUrl:video.currentSrc||video.src,videoCount:document.querySelectorAll('video').length});
}
function attach(video){
 if(controls.has(video))return;
 const host=document.createElement('rainy-video-control');host.style.cssText='position:fixed;z-index:2147483646;pointer-events:auto;display:none';
 const shadow=host.attachShadow({mode:'closed'}),style=document.createElement('style');style.textContent=css;
 const button=document.createElement('button');button.className='download';button.type='button';button.textContent='R · Татах';button.setAttribute('aria-label','RAINY програмаар энэ бичлэгийг татах');
 const panel=document.createElement('div');panel.className='panel';panel.hidden=true;
 const title=document.createElement('strong');title.textContent='RAINY · Бичлэг татах';
 const format=document.createElement('select');format.setAttribute('aria-label','Формат');for(const [v,t] of [['mp4','Видео · MP4'],['mp3','Аудио · MP3']]){const o=document.createElement('option');o.value=v;o.textContent=t;format.append(o);}
 const quality=document.createElement('select');quality.setAttribute('aria-label','Дээд чанар');for(const n of [360,480,720,1080,1440,2160]){const o=document.createElement('option');o.value=n;o.textContent=n+'p хүртэл';quality.append(o);}quality.value='1080';
 const audio=document.createElement('select');audio.setAttribute('aria-label','MP3 чанар');for(const n of [128,192,256,320]){const o=document.createElement('option');o.value=n;o.textContent=n+' kbps';audio.append(o);}audio.value='192';audio.hidden=true;
 const go=document.createElement('button');go.className='go';go.type='button';go.textContent='Дараалалд нэмэх';
 const note=document.createElement('span');note.className='note';note.textContent='Windows програмд шууд нэмнэ.';
 format.onchange=()=>{quality.hidden=format.value==='mp3';audio.hidden=format.value!=='mp3';};
 panel.append(title,format,quality,audio,go,note);shadow.append(style,button,panel);document.documentElement.append(host);controls.set(video,{host,panel});
 button.onclick=async e=>{e.stopPropagation();panel.hidden=!panel.hidden;if(!panel.hidden){try{const s=await rpc('inline-defaults');format.value=s.format;quality.value=s.quality;audio.value=s.audio_quality??192;format.onchange();}catch{note.textContent='Програм суусан эсэхийг шалгана уу.';}}};
 go.onclick=async e=>{
  e.stopPropagation();const url=source(video);
  if(!url){note.textContent='Энэ бичлэгийн нийтлэлийг тусад нь нээгээд дахин дарна уу.';return;}
  go.disabled=true;note.textContent='Шалгаж байна…';
  try{await rpc('inline-enqueue',{url,format:format.value,quality:Number(quality.value),audio_quality:Number(audio.value),title:document.title});note.textContent='✓ Дараалалд нэмэгдлээ. RAINY програмаас явцыг харна уу.';}
  catch(e){note.textContent=e.message;}
  finally{go.disabled=false;}
 };
}
function scan(){
 scheduled=false;
 for(const v of [...document.querySelectorAll('video')].slice(0,30))attach(v);
 for(const [v,c] of controls){
  if(!v.isConnected){c.host.remove();controls.delete(v);continue;}
  const r=v.getBoundingClientRect(),visible=isPlayingVideo(v)&&r.width>=160&&r.height>=90&&r.bottom>0&&r.top<innerHeight&&r.right>0&&r.left<innerWidth;
  c.host.style.display=visible?'block':'none';if(!visible)continue;
  const width=c.panel.hidden?104:235;c.host.style.left=Math.max(6,Math.min(innerWidth-width-8,r.right-width-12))+'px';c.host.style.top=Math.max(6,r.top+12)+'px';
 }
}
function schedule(){if(!scheduled){scheduled=true;requestAnimationFrame(scan);}}
for(const event of ['play','pause','ended','loadeddata'])document.addEventListener(event,schedule,true);
addEventListener('scroll',schedule,{passive:true,capture:true});addEventListener('resize',schedule,{passive:true});
new MutationObserver(schedule).observe(document.documentElement,{childList:true,subtree:true});setInterval(schedule,1200);scan();
