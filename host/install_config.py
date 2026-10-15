import base64,hashlib,re,json,sys

def extension_id(key):
    return ''.join(chr(ord('a')+int(c,16)) for c in hashlib.sha256(base64.b64decode(key,validate=True)).hexdigest()[:32])

def native_manifest(id,path):
    if not isinstance(id,str) or not re.fullmatch('[a-p]{32}',id): raise ValueError('Өргөтгөлийн ID буруу байна.')
    return {'name':'mn.rainy.downloader','description':'RAINY Downloader Windows host','path':path,'type':'stdio','allowed_origins':['chrome-extension://'+id+'/']}

if __name__=='__main__':
    from pathlib import Path
    root=Path(sys.argv[1]);id=sys.argv[2];paths=sys.argv[3:]
    (root/'native-config.json').write_text(json.dumps({'extension_id':id,'tool_paths':paths}),encoding='utf-8')
    (root/'mn.rainy.downloader.json').write_text(json.dumps(native_manifest(id,str(root/'start-host.cmd')),ensure_ascii=False,indent=2),encoding='utf-8')
