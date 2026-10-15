"""Create reproducible source delivery without caches, git history or secrets."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import sys,hashlib
root=Path(__file__).resolve().parent.parent
output=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else root.parent/'RAINY-Downloader-Windows.zip'
files=[]
for p in root.rglob('*'):
    if not p.is_file():continue
    relative=p.relative_to(root)
    if any(x in {'.git','__pycache__','.venv','node_modules'} for x in relative.parts):continue
    if p.suffix in {'.pyc','.db','.log','.zip'} or p.name=='native-config.json':continue
    files.append(p)
with ZipFile(output,'w',ZIP_DEFLATED) as z:
    for p in sorted(files):z.write(p,'RAINY-Downloader/'+p.relative_to(root).as_posix())
with ZipFile(output) as z:
    assert z.testzip() is None
    for p in ['INSTALL.cmd','UNINSTALL.cmd','README-MN.md','extension/manifest.json','host/native.py','windows/install.ps1','VALIDATION.md']:
        assert 'RAINY-Downloader/'+p in z.namelist(),p
print(f'{output}\nFiles: {len(files)}\nBytes: {output.stat().st_size}\nSHA256: {hashlib.sha256(output.read_bytes()).hexdigest()}')
