export const HOST='mn.rainy.downloader';
export function normalizeUrl(value){
 const u=new URL(String(value).trim());
 if(!['http:','https:'].includes(u.protocol)||u.username||u.password||u.port||!u.hostname.includes('.')||u.hostname==='localhost'||/\.(local|test|internal)$/.test(u.hostname)||/^(127\.|10\.|192\.168\.|169\.254\.|0\.)/.test(u.hostname))throw new Error('Нийтийн видео холбоос оруулна уу.');
 u.hash='';return u.href;
}
export function validateSettings(s){
 if(![360,480,720,1080,1440,2160].includes(Number(s.quality))||!['mp4','mp3'].includes(s.format))throw new Error('Тохиргоо буруу байна.');
 const audio_quality=Number(s.audio_quality??192);if(![128,192,256,320].includes(audio_quality))throw new Error('MP3 чанар буруу.');
 return {...s,quality:Number(s.quality),audio_quality,oneClick:!!s.oneClick};
}
export function progressText(n){return `${Number.isFinite(Number(n))?Math.min(100,Math.max(0,Math.round(Number(n)))):0}%`;}
export function friendlyError(v){
 const t=String(v||'');
 if(/forbidden|Access to/i.test(t))return 'Өргөтгөлийн ID тохирохгүй байна. Суулгацыг зөв ID-гаар дахин ажиллуулна уу.';
 if(/not found|exited|Failed to start|Native host|disconnected|receiving end/i.test(t))return 'Суулгац шаардлагатай. Windows туслах програмыг суулгаад Chrome-оо дахин нээнэ үү.';
 return t||'Үйлдэл амжилтгүй. Дахин оролдоно уу.';
}
export async function request(action,payload={}){
 const r=await chrome.runtime.sendMessage({action,payload});
 if(!r?.ok)throw new Error(friendlyError(r?.error));return r.data;
}
export function isContentSender(sender,extensionBase){return !!sender.tab&&!String(sender.url||'').startsWith(extensionBase);}
