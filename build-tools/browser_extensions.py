"""Build Chromium and Firefox development distributions from one UI source."""
from pathlib import Path
import json,re,shutil,sys,zipfile
ROOT=Path(__file__).resolve().parent.parent

def build(destination):
    destination=Path(destination);destination.mkdir(parents=True,exist_ok=True)
    for kind in ['chromium','firefox']:
        target=destination/kind
        if target.exists():shutil.rmtree(target)
        shutil.copytree(ROOT/'extension',target)
        if kind=='firefox':
            m=json.loads((target/'manifest.json').read_text(encoding='utf-8'));m.pop('key',None)
            m['background']={'scripts':['background-firefox.js']}
            m['browser_specific_settings']={'gecko':{'id':'downloader@rainy.local','strict_min_version':'128.0'}}
            (target/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            sources=[]
            for filename in ['shared.js','video-source.js','background.js']:
                text=(target/filename).read_text(encoding='utf-8');text=re.sub(r'^import .*?;\s*','',text,flags=re.M);text=re.sub(r'\bexport\s+','',text);sources.append(text)
            (target/'background-firefox.js').write_text('\n'.join(sources),encoding='utf-8')
        with zipfile.ZipFile(destination/(kind+'-development.zip'),'w',zipfile.ZIP_DEFLATED) as z:
            for p in sorted(target.rglob('*')):
                if p.is_file():z.write(p,p.relative_to(target).as_posix())
    return destination
if __name__=='__main__':build(Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'browser-extensions')
