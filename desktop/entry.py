"""Windowed EXE entry; worker and registration modes never open a GUI."""
import sys,json
from pathlib import Path

def main():
    args=sys.argv[1:]
    if '--worker' in args:
        from host.worker import main as worker
        worker();return
    if '--register' in args:
        from host.browser_install import register
        from host.runtime import ROOT
        register(ROOT);return
    if '--unregister' in args:
        from host.browser_install import unregister
        unregister();return
    if '--health-report' in args:
        from host.runtime import health
        h=health();Path(args[args.index('--health-report')+1]).write_text(json.dumps(h),encoding='utf-8');sys.exit(0 if h['ready'] else 1)
    from desktop.app import main as gui
    gui()
if __name__=='__main__':
    try:main()
    except Exception:
        import traceback,os
        data=Path(os.environ.get('LOCALAPPDATA',str(Path.home())))/'RAINYDownloader'/'data';data.mkdir(parents=True,exist_ok=True)
        (data/'last-error.log').write_text(traceback.format_exc(),encoding='utf-8')
        if not any(a in sys.argv for a in ('--worker','--register','--unregister','--health-report')):
            try:
                from tkinter import messagebox
                messagebox.showerror('RAINY','Програм эхлэхэд алдаа гарлаа. data/last-error.log файлыг шалгана уу.')
            except Exception:pass
        sys.exit(1)
