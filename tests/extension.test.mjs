import test from 'node:test';
import assert from 'node:assert/strict';
import {normalizeUrl,validateSettings,progressText,friendlyError} from '../extension/shared.js';
test('public URL validation',()=>{
 assert.equal(normalizeUrl(' https://youtu.be/abc#x '),'https://youtu.be/abc');
 for(const u of ['file:///x','http://localhost/a','https://u:p@youtube.com/a','https://example.com:123/a']) assert.throws(()=>normalizeUrl(u));
});
test('settings and progress',()=>{
 assert.equal(validateSettings({quality:720,format:'mp4',oneClick:false}).quality,720);
 assert.throws(()=>validateSettings({quality:-2,format:'mp4'}));
 assert.equal(progressText(50.12),'50%'); assert.equal(progressText(NaN),'0%');
});
test('native host error in Mongolian',()=>{
 assert.match(friendlyError('Specified native messaging host not found.'),/Суулгац/);
 assert.match(friendlyError('Access to the specified native messaging host is forbidden.'),/ID/);
});
import {resolveVideoUrl,inlinePayload} from '../extension/video-source.js';
test('specific platform permalinks',()=>{
 assert.equal(resolveVideoUrl({pageUrl:'https://www.youtube.com/watch?v=abc&list=123',anchors:[]}), 'https://www.youtube.com/watch?v=abc');
 assert.equal(resolveVideoUrl({pageUrl:'https://www.instagram.com/',anchors:['https://www.instagram.com/reel/ABC/']}),'https://www.instagram.com/reel/ABC/');
 assert.equal(resolveVideoUrl({pageUrl:'https://x.com/home',anchors:['https://x.com/user/status/123']}),'https://x.com/user/status/123');
 assert.equal(resolveVideoUrl({pageUrl:'https://www.tiktok.com/foryou',anchors:['https://www.tiktok.com/@u/video/123']}),'https://www.tiktok.com/@u/video/123');
 assert.equal(resolveVideoUrl({pageUrl:'https://www.facebook.com/',anchors:['https://www.facebook.com/reel/123']}),'https://www.facebook.com/reel/123');
});
test('ambiguous feeds and blob never enqueue guessed URLs',()=>{
 assert.equal(resolveVideoUrl({pageUrl:'https://www.instagram.com/',anchors:[],mediaUrl:'blob:abc'}),null);
 assert.equal(resolveVideoUrl({pageUrl:'https://example.com/feed',videoCount:3,anchors:[],mediaUrl:'blob:abc'}),null);
 assert.equal(resolveVideoUrl({pageUrl:'https://example.com/video',videoCount:1,anchors:[],mediaUrl:'https://cdn.example.com/a.mp4'}),'https://cdn.example.com/a.mp4');
});
test('content payload validation',()=>{
 assert.equal(inlinePayload({url:'https://youtu.be/a',format:'mp4',quality:720}).quality,720);
 assert.throws(()=>inlinePayload({url:'file:///a',format:'mp4',quality:720}));
 assert.throws(()=>inlinePayload({url:'https://youtu.be/a',format:'exe',quality:720}));
});
import {isContentSender} from '../extension/shared.js';
test('extension tabs retain privileged UI actions',()=>{
 const base='chrome-extension://abc/';
 assert.equal(isContentSender({tab:{id:1},url:base+'options.html'},base),false);
 assert.equal(isContentSender({tab:{id:1},url:'https://youtube.com/watch?v=x'},base),true);
 assert.equal(isContentSender({url:base+'popup.html'},base),false);
});
test('ambiguous card links never select arbitrary first video',()=>{
 assert.equal(resolveVideoUrl({pageUrl:'https://x.com/home',anchors:['https://x.com/a/status/111','https://x.com/b/status/222']}),null);
 assert.equal(resolveVideoUrl({pageUrl:'https://www.youtube.com/',anchors:['https://www.youtube.com/watch?v=a','https://www.youtube.com/watch?v=b']}),null);
 assert.equal(resolveVideoUrl({pageUrl:'https://x.com/a/status/111',anchors:['https://x.com/b/status/222','https://x.com/a/status/111']}),null);
});
import {isPlayingVideo} from '../extension/video-source.js';
test('download control only for actively playing video',()=>{
 assert.equal(isPlayingVideo({paused:false,ended:false,readyState:3,currentTime:1,videoWidth:1920,videoHeight:1080}),true);
 for(const diff of [{paused:true},{ended:true},{readyState:1},{currentTime:0},{videoWidth:0}])assert.equal(isPlayingVideo({paused:false,ended:false,readyState:3,currentTime:1,videoWidth:1920,videoHeight:1080,...diff}),false);
});
