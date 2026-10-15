"""Windows CI smoke test of the packaged console bridge with framed binary stdio."""
import io,subprocess,sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from host.protocol import write_frame,read_frame
from host.browser_install import CHROMIUM_ID
root=Path(sys.argv[1]).resolve();stream=io.BytesIO();write_frame(stream,{'id':1,'action':'health','payload':{}})
p=subprocess.run([str(root/'RAINY.Native.exe'),'chrome-extension://'+CHROMIUM_ID+'/'],input=stream.getvalue(),capture_output=True,timeout=50)
if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace'))
r=read_frame(io.BytesIO(p.stdout))
if not r or not r.get('ok') or not r.get('data',{}).get('ready'):raise RuntimeError(repr(r))
print('Packaged native host roundtrip: PASS')
