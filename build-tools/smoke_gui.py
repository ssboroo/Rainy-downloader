"""Windows CI launch smoke: packaged GUI must create its window without crashing."""
from pathlib import Path
import subprocess,sys,time
from pywinauto import Application
exe=Path(sys.argv[1]).resolve();p=subprocess.Popen([str(exe)])
try:
    app=Application(backend='uia').connect(process=p.pid,timeout=20)
    window=app.window(title='RAINY Татагч')
    window.wait('exists visible',timeout=20)
    time.sleep(2)
    if p.poll() is not None:raise RuntimeError('Packaged GUI exited during startup')
    window.capture_as_image().save(exe.parent.parent/'RAINY-Interface.png')
    print('Packaged desktop window launch: PASS')
finally:
    if p.poll() is None:p.terminate()
    p.wait(timeout=10)
