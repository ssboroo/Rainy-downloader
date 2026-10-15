import {request,validateSettings,friendlyError} from './shared.js';
const $=id=>document.getElementById(id);
$('id').textContent=chrome.runtime.id;
function say(t,e=false){$('message').hidden=false;$('message').textContent=t;$('message').classList.toggle('error',e);}
$('options').onsubmit=async e=>{e.preventDefault();$('save').disabled=true;try{const values=validateSettings({folder:$('folder').value.trim(),format:$('format').value,quality:Number($('quality').value),audio_quality:Number($('audio-quality').value),oneClick:$('oneClick').checked});await request('settings',values);say('Тохиргоо хадгалагдлаа.');}catch(e){say(friendlyError(e.message),true);}finally{$('save').disabled=false;}};
(async()=>{try{const s=await request('snapshot');for(const k of ['folder','format','quality'])$(k).value=s.settings[k];$('audio-quality').value=s.settings.audio_quality??192;$('format').onchange();$('oneClick').checked=s.settings.oneClick;const h=await request('health');$('health').textContent=`${h.message} · yt-dlp ${h.yt_dlp||'суулгаагүй'} · FFmpeg ${h.ffmpeg?'✓':'✕'} · Deno ${h.deno?'✓':'✕'}`;}catch(e){say(friendlyError(e.message),true);$('health').textContent='Windows туслах програмтай холбогдоогүй.';}})();

const origins=['http://*/*','https://*/*'];
async function controlStatus(){const granted=await chrome.permissions.contains({origins});$('controls-status').textContent=granted?'✓ Зөвшөөрөгдсөн. Видео хуудсаа шинэчилнэ үү.':'Сайтын хандалт олгоогүй. Товч харагдахгүй.';}
$('enable-controls').onclick=async()=>{try{await chrome.permissions.request({origins});await controlStatus();}catch(e){say(e.message,true);}};
$('disable-controls').onclick=async()=>{try{await chrome.permissions.remove({origins});await controlStatus();say('Шинэ табуудад товч идэвхгүй болно. Нээлттэй хуудсаа шинэчилнэ үү.');}catch(e){say(e.message,true);}};
controlStatus();

$('format').onchange=()=>{$('quality').hidden=$('format').value==='mp3';$('audio-quality').hidden=$('format').value!=='mp3';};
