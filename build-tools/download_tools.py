"""Fetch Windows tools from official GitHub releases; require release SHA256 digest."""
from pathlib import Path
from urllib.request import urlopen,Request
from urllib.parse import urlsplit
import fnmatch,hashlib,json,tempfile,zipfile,shutil,sys
AGENT='RAINY-Windows-Build/2.0'

def read(url):
    if urlsplit(url).scheme!='https':raise ValueError('HTTPS required')
    return urlopen(Request(url,headers={'User-Agent':AGENT}),timeout=90)

def asset(repo,pattern,out):
    with read('https://api.github.com/repos/'+repo+'/releases/latest') as r:release=json.load(r)
    matches=[a for a in release['assets'] if fnmatch.fnmatch(a['name'],pattern)]
    if len(matches)!=1:raise ValueError(f'Expected one release asset: {repo}/{pattern}; found {len(matches)}')
    a=matches[0];digest=a.get('digest') or ''
    if not digest.startswith('sha256:'):raise ValueError(f'Upstream release has no SHA256 digest for {a["name"]}; review it rather than bypass verification')
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True);h=hashlib.sha256()
    try:
        with read(a['browser_download_url']) as r,open(out,'wb') as f:
            while True:
                chunk=r.read(1024*1024)
                if not chunk:break
                f.write(chunk);h.update(chunk)
        if h.hexdigest()!=digest.split(':',1)[1]:raise ValueError('SHA256 verification failed: '+a['name'])
    except Exception:
        out.unlink(missing_ok=True);raise
    return {'repository':repo,'tag':release['tag_name'],'asset':a['name'],'sha256':h.hexdigest()}

def extract_binary(archive,name,target):
    with zipfile.ZipFile(archive) as z:
        matches=[n for n in z.namelist() if Path(n).name.lower()==name.lower()]
        if len(matches)!=1:raise ValueError('Expected exactly one binary: '+name)
        with z.open(matches[0]) as src,open(target,'wb') as dst:shutil.copyfileobj(src,dst)
        # No other zip paths are extracted.

def main(destination):
    tools=Path(destination);tools.mkdir(parents=True,exist_ok=True);versions=[]
    versions.append(asset('yt-dlp/yt-dlp','yt-dlp.exe',tools/'yt-dlp.exe'))
    with tempfile.TemporaryDirectory() as d:
        deno=Path(d)/'deno.zip';versions.append(asset('denoland/deno','deno-x86_64-pc-windows-msvc.zip',deno));extract_binary(deno,'deno.exe',tools/'deno.exe')
        ff=Path(d)/'ffmpeg.zip';versions.append(asset('GyanD/codexffmpeg','*essentials_build.zip',ff))
        for name in ['ffmpeg.exe','ffprobe.exe']:extract_binary(ff,name,tools/name)
    (tools/'versions.json').write_text(json.dumps(versions,indent=2),encoding='utf-8')
    return versions
if __name__=='__main__':main(sys.argv[1])
