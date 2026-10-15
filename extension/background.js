import {HOST,friendlyError,isContentSender} from './shared.js';
import {inlinePayload} from './video-source.js';
function native(message,respond,transform=v=>v){
 chrome.runtime.sendNativeMessage(HOST,message,r=>{const e=chrome.runtime.lastError;respond(e?{ok:false,error:friendlyError(e.message)}:r?.ok?{ok:true,data:transform(r.data)}:r||{ok:false,error:'Холболт тасарсан.'});});
}
chrome.runtime.onMessage.addListener((message,sender,respond)=>{
 if(sender.id!==chrome.runtime.id)return false;
 if(isContentSender(sender,chrome.runtime.getURL(''))){
  if(message?.action==='inline-defaults'){native({action:'snapshot',payload:{}},respond,data=>({format:data.settings.format,quality:data.settings.quality,audio_quality:data.settings.audio_quality}));return true;}
  if(message?.action!=='inline-enqueue'){respond({ok:false,error:'Зөвшөөрөгдөөгүй үйлдэл.'});return false;}
  try{
   const payload=inlinePayload(message.payload||{});
   // Inspect first: ambiguous playlists are never silently expanded or guessed.
   chrome.runtime.sendNativeMessage(HOST,{action:'inspect',payload:{url:payload.url}},r=>{
    const e=chrome.runtime.lastError;
    if(e||!r?.ok){respond({ok:false,error:friendlyError(e?.message||r?.error)});return;}
    if(r.data.playlist){respond({ok:false,error:'Олон бичлэгтэй холбоос байна. RAINY програмд нээгээд сонгоно уу.'});return;}
    native({action:'enqueue',payload:{...payload,title:r.data.title}},respond,job=>({id:job.id}));
   });return true;
  }catch(e){respond({ok:false,error:e.message});return false;}
 }
 const allowed=['health','inspect','enqueue','snapshot','cancel','settings','open_folder'];
 if(!allowed.includes(message?.action)){respond({ok:false,error:'Танигдаагүй үйлдэл.'});return false;}
 native(message,respond);return true;
});
const ORIGINS=['http://*/*','https://*/*'];
async function syncControls(){
 try{
  const granted=await chrome.permissions.contains({origins:ORIGINS});
  const scripts=await chrome.scripting.getRegisteredContentScripts({ids:['rainy-video-controls']});
  if(granted&&!scripts.length)await chrome.scripting.registerContentScripts([{id:'rainy-video-controls',matches:ORIGINS,js:['bootstrap.js'],allFrames:true,runAt:'document_idle',persistAcrossSessions:true}]);
  if(!granted&&scripts.length)await chrome.scripting.unregisterContentScripts({ids:['rainy-video-controls']});
 }catch(e){console.warn('RAINY browser controls:',e.message);}
}
chrome.runtime.onInstalled.addListener(syncControls);chrome.runtime.onStartup.addListener(syncControls);chrome.permissions.onAdded.addListener(syncControls);chrome.permissions.onRemoved.addListener(syncControls);
