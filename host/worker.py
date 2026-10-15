"""Single independent worker. Queue and progress survive popup closure."""
import json, os, sys, time, subprocess, threading, queue
from pathlib import Path
from host.storage import Store
from host.core import build_args
from host.errors import download_error
from host.runtime import DATA, tools, subprocess_options, subprocess_environment

def parse_progress(line):
    if not line.startswith('RAINY_PROGRESS:'): return None
    try:
        p=json.loads(line.split(':',1)[1]); total=p.get('total_bytes') or p.get('total_bytes_estimate') or 0
        return {'progress':round(min(99,100*(p.get('downloaded_bytes') or 0)/total),1) if total else 0,'speed':p.get('speed'),'eta':p.get('eta')}
    except (ValueError,TypeError,AttributeError): return None

def safe_output(value,folder):
    p=Path(value).resolve(); base=Path(folder).resolve()
    if not p.is_relative_to(base): raise ValueError('Гаралтын файлын зам буруу.')
    return str(p)

def stop_process(p):
    if p.poll() is not None: return
    if os.name=='nt':
        subprocess.run(['taskkill','/PID',str(p.pid),'/T','/F'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,**subprocess_options())
    else:
        import signal
        try: os.killpg(p.pid,signal.SIGTERM)
        except ProcessLookupError: pass
    try: p.wait(timeout=8)
    except subprocess.TimeoutExpired: p.kill(); p.wait(timeout=3)

def acquire_lock(path):
    f=open(path,'a+b'); f.seek(0); f.write(b'0'); f.flush(); f.seek(0)
    try:
        if os.name=='nt':
            import msvcrt
            msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1)
        else:
            import fcntl
            fcntl.flock(f.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        return f
    except OSError: f.close(); return None

def download(store,job):
    if (store.get(job['id']) or {}).get('status')!='queued': return
    Path(job['folder']).mkdir(parents=True,exist_ok=True)
    p=subprocess.Popen(build_args(job,tools()),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace',bufsize=1,
                       start_new_session=os.name!='nt',env=subprocess_environment(),**subprocess_options())
    store.update(job['id'],{'status':'downloading','pid':p.pid})
    lines=queue.Queue()
    def reader():
        try:
            for line in p.stdout: lines.put(line.rstrip())
        finally: lines.put(None)
    threading.Thread(target=reader,daemon=True).start()
    output=''; errors=[]; last=time.monotonic(); last_progress=0
    try:
        while True:
            current=store.get(job['id'])
            if not current or current['status']=='cancelled': stop_process(p); return
            try: line=lines.get(timeout=.3)
            except queue.Empty:
                if time.monotonic()-last>180: stop_process(p); raise ValueError('Таталт удаан хариу өгөөгүй тул зогслоо. Дахин оролдоно уу.')
                continue
            if line is None: break
            last=time.monotonic(); progress=parse_progress(line)
            if progress and last-last_progress>.4:
                store.update(job['id'],progress); last_progress=last
            if line.startswith('RAINY_FILE:'): output=safe_output(line.split(':',1)[1],job['folder'])
            if line.startswith('[Merger]') or line.startswith('[ExtractAudio]'): store.update(job['id'],{'status':'processing'})
            if 'ERROR:' in line: errors.append(line[-700:]); errors=errors[-3:]
        code=p.wait(timeout=10)
        current=store.get(job['id'])
        if current['status']=='cancelled': return
        if code or not output or not Path(output).is_file():
            raise ValueError(download_error(job['url'],' '.join(errors)))
        store.update(job['id'],{'status':'done','progress':100,'output_path':output,'speed':None,'eta':None,'error':''})
    finally:
        stop_process(p)
        if p.stdout: p.stdout.close()

def main():
    DATA.mkdir(parents=True,exist_ok=True); lock=acquire_lock(DATA/'worker.lock')
    if lock is None: return
    store=Store(DATA/'queue.db'); store.recover(); idle=time.monotonic()
    while True:
        job=store.next()
        if not job:
            if time.monotonic()-idle>90: return
            time.sleep(.5); continue
        idle=time.monotonic()
        try: download(store,job)
        except Exception as e:
            current=(store.get(job['id']) or {})
            if current.get('status')!='cancelled': store.update(job['id'],{'status':'error','error':str(e)[:1400]})

if __name__=='__main__': main()
