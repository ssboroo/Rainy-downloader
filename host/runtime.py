"""Runtime locations work in Python source and packaged Windows applications."""
import os,sys,shutil,subprocess,json
from pathlib import Path
from functools import lru_cache
FROZEN=bool(getattr(sys,'frozen',False))
ROOT=Path(sys.executable).resolve().parent if FROZEN else Path(__file__).resolve().parent.parent
RESOURCE_ROOT=Path(getattr(sys,'_MEIPASS',ROOT))
try:
    config=json.loads((ROOT/'native-config.json').read_text(encoding='utf-8-sig'))
    configured=[p for p in config.get('tool_paths',[]) if isinstance(p,str) and Path(p).is_dir()]
except (OSError,ValueError,TypeError): configured=[]
if (ROOT/'tools').is_dir():configured.insert(0,str(ROOT/'tools'))
os.environ['PATH']=os.pathsep.join(configured+[os.environ.get('PATH','')])
DATA=Path(os.environ.get('LOCALAPPDATA',str(Path.home()/'.local/share')))/'RAINYDownloader'/'data'

def subprocess_environment():
    return {**os.environ,'PYTHONUTF8':'1','PYTHONIOENCODING':'utf-8'}

def subprocess_options():
    return {'creationflags':subprocess.CREATE_NO_WINDOW} if os.name=='nt' else {}

def executable_command(mode,frozen=None,exe=None):
    frozen=FROZEN if frozen is None else frozen;exe=exe or sys.executable
    if frozen:
        # The native console helper must spawn GUI executable in worker-only mode.
        binary=str(ROOT/'RAINY.exe') if Path(exe).stem.lower()=='rainy.native' else exe
        return [binary,'--'+mode]
    return [exe,'-m','host.'+mode]

def tool_command(root=None,python=None,frozen=None):
    frozen=FROZEN if frozen is None else frozen
    candidate=Path(root or ROOT)/'tools'/'yt-dlp.exe'
    if candidate.is_file():return [str(candidate)]
    if frozen:raise FileNotFoundError('Багцын tools/yt-dlp.exe олдсонгүй. Програмыг дахин суулгана уу.')
    return [python or sys.executable,'-m','yt_dlp']

def tools():return {'yt_dlp':tool_command()}

@lru_cache(maxsize=1)
def health():
    results={}
    commands={'ffmpeg':['ffmpeg','-version'],'ffprobe':['ffprobe','-version'],'deno':['deno','--version']}
    try:commands['yt_dlp']=tool_command()+['--version']
    except FileNotFoundError:results['yt_dlp']=None
    for name,command in commands.items():
        try:
            r=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=8,**subprocess_options())
            results[name]=(r.stdout.strip().splitlines() or [''])[0][:180] if r.returncode==0 else None
        except (OSError,subprocess.TimeoutExpired):results[name]=None
    results['ready']=all(results.values())
    results['message']='Татахад бэлэн' if results['ready'] else 'Таталтын хэрэгсэл дутуу эсвэл ажиллахгүй байна. Програмыг дахин суулгана уу.'
    return results

def ensure_worker():
    DATA.mkdir(parents=True,exist_ok=True)
    flags=(subprocess.DETACHED_PROCESS|subprocess.CREATE_NEW_PROCESS_GROUP|subprocess.CREATE_NO_WINDOW) if os.name=='nt' else 0
    subprocess.Popen(executable_command('worker'),cwd=ROOT,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
                     creationflags=flags,start_new_session=os.name!='nt')
