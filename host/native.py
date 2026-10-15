"""Native Messaging RPC. Never print diagnostic text to stdout."""
import json, os, sys, subprocess
from pathlib import Path
from urllib.parse import urlsplit
from host.protocol import read_frame, write_frame
from host.storage import Store
from host.core import normalize_url
from host.runtime import DATA, ROOT, health, ensure_worker, tools, subprocess_options

def check_origin(origin,extension_id):
    if origin!='chrome-extension://'+extension_id+'/': raise ValueError('Өргөтгөлийн эрх буруу.')

def summarize_info(info):
    entries=info.get('entries')
    if entries is not None:
        out=[]
        for e in entries:
            if not e: continue
            url=e.get('webpage_url') or e.get('url') or ''
            try: url=normalize_url(url)
            except ValueError: continue
            out.append({'url':url,'title':str(e.get('title') or url)[:200]})
        return {'playlist':True,'title':str(info.get('title') or 'Олон бичлэг')[:200],'count':len(out),'entries':out[:100],'limited':len(out)>=100}
    thumb=info.get('thumbnail') or ''
    try:
        if urlsplit(thumb).scheme!='https': thumb=''
    except ValueError: thumb=''
    heights=sorted({int(f['height']) for f in info.get('formats',[]) if isinstance(f.get('height'),(int,float)) and f['height']>0})
    return {'playlist':False,'title':str(info.get('title') or 'Бичлэг')[:300],'thumbnail':thumb,'duration':info.get('duration'),'heights':heights,'site':str(info.get('extractor_key') or '')[:100]}

def inspect(url):
    url=normalize_url(url)
    args=[*tools()['yt_dlp'],'--ignore-config','--encoding','utf-8','--dump-single-json','--flat-playlist','--playlist-end','100','--skip-download','--no-warnings','--socket-timeout','15','--retries','1','--',url]
    try:
        p=subprocess.run(args,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=65,**subprocess_options())
    except subprocess.TimeoutExpired: raise ValueError('Холбоос шалгах хугацаа дууслаа. Дахин оролдоно уу.')
    if p.returncode: raise ValueError('Бичлэгийн мэдээлэл авах боломжгүй. Нийтэд нээлттэй холбоос эсэхийг шалгана уу. '+p.stderr[-700:])
    return summarize_info(json.loads(p.stdout))

def dispatch(action,payload,store):
    if action=='health': return health()
    if action=='snapshot':
        result=store.snapshot()
        if any(j['status']=='queued' for j in result['jobs']): ensure_worker()
        return result
    if action=='settings': return store.settings(payload)
    if action=='inspect':
        if not health()['ready']: raise ValueError(health()['message'])
        return inspect(payload['url'])
    if action=='enqueue':
        h=health()
        if not h['ready']: raise ValueError(h['message'])
        job=store.enqueue(payload); ensure_worker(); return job
    if action=='cancel':
        job=store.get(payload.get('id'))
        if not job or job['status'] not in ('queued','downloading','processing'): raise ValueError('Цуцлах идэвхтэй таталт олдсонгүй.')
        store.update(job['id'],{'status':'cancelled','speed':None,'eta':None}); return {'cancelled':True}
    if action=='open_folder':
        job=store.get(payload.get('id'))
        if not job: raise ValueError('Таталт олдсонгүй.')
        folder=Path(job['folder']).resolve()
        if not folder.is_dir(): raise ValueError('Хавтас олдсонгүй.')
        if os.name!='nt': raise ValueError('Энэ үйлдэл Windows-д зориулагдсан.')
        os.startfile(str(folder)); return {'opened':True}
    raise ValueError('Танигдаагүй үйлдэл.')

def main(argv=None):
    argv=sys.argv[1:] if argv is None else argv
    if os.name=='nt':
        import msvcrt
        msvcrt.setmode(sys.stdin.fileno(),os.O_BINARY); msvcrt.setmode(sys.stdout.fileno(),os.O_BINARY)
    try:
        from host.runtime import FROZEN
        if FROZEN:
            from host.browser_install import CHROMIUM_ID,FIREFOX_ID
            # Chrome passes extension origin first; Firefox passes manifest path and addon ID.
            if argv and argv[0].startswith('chrome-extension://'):check_origin(argv[0],CHROMIUM_ID)
            elif len(argv)<2 or argv[1]!=FIREFOX_ID:return
        else:
            cfg=json.loads((ROOT/'native-config.json').read_text(encoding='utf-8-sig'))
            check_origin(argv[0] if argv else '',cfg['extension_id'])
    except Exception:return
    store=Store(DATA/'queue.db')
    while True:
        try: m=read_frame(sys.stdin.buffer)
        except ValueError: break
        if m is None: break
        try:
            payload=m.get('payload',{})
            if not isinstance(payload,dict): raise ValueError('Хүсэлтийн бүтэц буруу.')
            data=dispatch(m.get('action'),payload,store); result={'id':m.get('id'),'ok':True,'data':data}
        except Exception as e: result={'id':m.get('id'),'ok':False,'error':str(e)[:1800]}
        try: write_frame(sys.stdout.buffer,result)
        except ValueError:
            try: write_frame(sys.stdout.buffer,{'id':m.get('id'),'ok':False,'error':'Хариу хэт том байна. Цөөн бичлэгээр дахин оролдоно уу.'})
            except (BrokenPipeError,OSError,ValueError): break
        except (BrokenPipeError,OSError): break
if __name__=='__main__': main()
