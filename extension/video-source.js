import {normalizeUrl,validateSettings} from './shared.js';
const isHost=(h,d)=>h===d||h.endsWith('.'+d);
function permalink(value,site){
 try{
  const u=new URL(value);const h=u.hostname;
  if(!/^https?:$/.test(u.protocol))return null;
  if(site==='youtube'&&(isHost(h,'youtube.com')||h==='youtu.be')){
   if(u.pathname==='/watch'&&u.searchParams.get('v'))return `${u.origin}/watch?v=${encodeURIComponent(u.searchParams.get('v'))}`;
   if(/^\/(shorts|live)\/[^/]+/.test(u.pathname)||h==='youtu.be')return normalizeUrl(u.href);
  }
  if(site==='instagram'&&isHost(h,'instagram.com')&&/^\/(p|reel|reels)\/[^/]+/.test(u.pathname))return normalizeUrl(u.origin+u.pathname);
  if(site==='facebook'&&isHost(h,'facebook.com')&&(/^\/reel\/[^/]+/.test(u.pathname)||/\/videos\/[^/]+/.test(u.pathname)||u.pathname==='/watch/'&&u.searchParams.get('v')))return normalizeUrl(u.href);
  if(site==='x'&&(isHost(h,'x.com')||isHost(h,'twitter.com'))&&/^\/[^/]+\/status\/\d+/.test(u.pathname))return normalizeUrl(u.origin+u.pathname.replace(/\/video\/\d+.*$/,''));
  if(site==='tiktok'&&isHost(h,'tiktok.com')&&/^\/@[^/]+\/video\/\d+/.test(u.pathname))return normalizeUrl(u.origin+u.pathname);
 }catch{}return null;
}
export function resolveVideoUrl({pageUrl,anchors=[],mediaUrl='',videoCount=1}){
 let page;try{page=new URL(pageUrl);}catch{return null;}
 const h=page.hostname;
 const site=isHost(h,'youtube.com')||h==='youtu.be'?'youtube':isHost(h,'instagram.com')?'instagram':isHost(h,'facebook.com')?'facebook':isHost(h,'x.com')||isHost(h,'twitter.com')?'x':isHost(h,'tiktok.com')?'tiktok':null;
 if(site){const candidates=new Set(anchors.map(value=>permalink(value,site)).filter(Boolean));if(candidates.size>1)return null;if(candidates.size===1)return [...candidates][0];return permalink(pageUrl,site);}
 try{if(/^https?:/.test(mediaUrl))return normalizeUrl(mediaUrl);}catch{}
 try{return videoCount===1?normalizeUrl(pageUrl):null;}catch{return null;}
}
export function inlinePayload(p){
 const settings=validateSettings({format:p.format,quality:p.quality});
 return {url:normalizeUrl(p.url),format:settings.format,quality:settings.quality,title:String(p.title||'').slice(0,300)};
}
