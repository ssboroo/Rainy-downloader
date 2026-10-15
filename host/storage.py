"""Small durable queue shared by native host and worker."""
import json, sqlite3, uuid, time
from pathlib import Path
from host.core import normalize_url
DEFAULTS={'folder':str(Path.home()/'Downloads'/'RAINY'),'quality':1080,'format':'mp4','oneClick':False,'audio_quality':192,'showFloating':False}
class ClosingConnection(sqlite3.Connection):
    def __exit__(self,exc_type,exc_value,traceback):
        try:return super().__exit__(exc_type,exc_value,traceback)
        finally:self.close()

class Store:
    def __init__(self,path):
        self.path=str(path); Path(path).parent.mkdir(parents=True,exist_ok=True)
        with self.db() as c:
            c.execute('CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, data TEXT NOT NULL)')
            c.execute('CREATE TABLE IF NOT EXISTS settings (id INTEGER PRIMARY KEY, data TEXT NOT NULL)')
    def db(self):
        c=sqlite3.connect(self.path,timeout=15,factory=ClosingConnection)
        try:c.execute('PRAGMA journal_mode=WAL');return c
        except Exception:c.close();raise
    def settings(self,values=None):
        with self.db() as c:
            row=c.execute('SELECT data FROM settings WHERE id=1').fetchone()
            data={**DEFAULTS,**(json.loads(row[0]) if row else {})}
            if values is not None:
                data.update({k:v for k,v in values.items() if k in DEFAULTS})
                if data['quality'] not in (360,480,720,1080,1440,2160) or data['format'] not in ('mp3','mp4') or not isinstance(data['oneClick'],bool) or not isinstance(data['showFloating'],bool) or data['audio_quality'] not in (128,192,256,320): raise ValueError('Тохиргооны сонголт буруу.')
                if not isinstance(data['folder'],str) or len(data['folder'])>1024: raise ValueError('Хавтасны зам хэт урт байна.')
                p=Path(data['folder']).expanduser()
                if not p.is_absolute(): raise ValueError('Хадгалах хавтасны бүтэн замыг оруулна уу.')
                data['folder']=str(p)
                c.execute('INSERT OR REPLACE INTO settings VALUES (1,?)',(json.dumps(data),))
            return data
    def snapshot(self):
        with self.db() as c:
            all_jobs=[json.loads(r[0]) for r in c.execute('SELECT data FROM jobs ORDER BY rowid DESC')]
        active=[j for j in reversed(all_jobs) if j['status'] in ('queued','downloading','processing','interrupted')]
        history=[j for j in all_jobs if j['status'] not in ('queued','downloading','processing','interrupted')]
        jobs=active[:50]+history[:50]
        result={'jobs':jobs,'settings':self.settings(),'active_count':sum(j['status'] in ('queued','downloading','processing') for j in active),'omitted':len(all_jobs)-len(jobs)}
        while len(json.dumps(result,ensure_ascii=False).encode('utf-8'))>800000 and jobs:
            jobs.pop(); result['omitted']+=1
        return result
    def enqueue(self,job):
        data={**self.settings(),**job}; data['url']=normalize_url(data['url'])
        if data['format'] not in ('mp3','mp4') or data['quality'] not in (360,480,720,1080,1440,2160) or data['audio_quality'] not in (128,192,256,320): raise ValueError('Таталтын тохиргоо буруу.')
        if not isinstance(data['folder'],str) or len(data['folder'])>1024: raise ValueError('Хавтасны зам хэт урт байна.')
        folder=Path(data['folder']).expanduser()
        if not folder.is_absolute(): raise ValueError('Хавтасны бүтэн зам шаардлагатай.')
        data['folder']=str(folder)
        with self.db() as c:
            c.execute('BEGIN IMMEDIATE')
            jobs=[json.loads(r[0]) for r in c.execute('SELECT data FROM jobs')]
            if any(j['url']==data['url'] and j['status'] in ('queued','downloading','processing') for j in jobs): raise ValueError('Энэ бичлэг таталтын дараалалд байна.')
            data={k:data[k] for k in ('url','folder','quality','format','audio_quality')}
            data.update(id=uuid.uuid4().hex,title=str(job.get('title') or data['url'])[:300],status='queued',progress=0,speed=None,eta=None,error='',output_path='',created=time.time())
            c.execute('INSERT INTO jobs VALUES (?,?)',(data['id'],json.dumps(data)))
        return data
    def get(self,id):
        with self.db() as c:
            row=c.execute('SELECT data FROM jobs WHERE id=?',(id,)).fetchone()
        return json.loads(row[0]) if row else None
    def update(self,id,fields):
        allowed={'status','progress','speed','eta','error','output_path','title','pid'}
        with self.db() as c:
            c.execute('BEGIN IMMEDIATE'); row=c.execute('SELECT data FROM jobs WHERE id=?',(id,)).fetchone()
            if not row: raise ValueError('Таталт олдсонгүй.')
            data=json.loads(row[0])
            if data['status']=='cancelled': return
            bounded={k:v for k,v in fields.items() if k in allowed}
            for key,limit in [('error',1400),('title',300),('output_path',2048)]:
                if key in bounded: bounded[key]=str(bounded[key])[:limit]
            data.update(bounded)
            c.execute('UPDATE jobs SET data=? WHERE id=?',(json.dumps(data),id))
    def recover(self):
        with self.db() as c:
            jobs=[json.loads(r[0]) for r in c.execute('SELECT data FROM jobs')]
        for j in jobs:
            if j['status'] in ('downloading','processing'): self.update(j['id'],{'status':'interrupted','error':'Таталт тасарсан. Дахин дараалалд оруулна уу.'})
    def next(self):
        with self.db() as c:
            for row in c.execute('SELECT data FROM jobs ORDER BY rowid'):
                j=json.loads(row[0])
                if j['status']=='queued': return j
