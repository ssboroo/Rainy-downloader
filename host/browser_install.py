"""Per-user host registration. This never installs or silently enables an extension."""
import json,os,re
from pathlib import Path
CHROMIUM_ID='fpkmjpbhnffggibaenfhnacakkcpfbmc'
FIREFOX_ID='downloader@rainy.local'
REGISTRY={'Chrome':r'Software\Google\Chrome\NativeMessagingHosts\mn.rainy.downloader',
          'Edge':r'Software\Microsoft\Edge\NativeMessagingHosts\mn.rainy.downloader',
          'Brave':r'Software\BraveSoftware\Brave-Browser\NativeMessagingHosts\mn.rainy.downloader',
          'Opera':r'Software\Opera Software\NativeMessagingHosts\mn.rainy.downloader',
          'Firefox':r'Software\Mozilla\NativeMessagingHosts\mn.rainy.downloader'}

def manifests(root,chromium_id=CHROMIUM_ID):
    if not re.fullmatch('[a-p]{32}',chromium_id):raise ValueError('Өргөтгөлийн ID буруу.')
    common={'name':'mn.rainy.downloader','description':'RAINY browser bridge','type':'stdio','path':str(Path(root)/'RAINY.Native.exe')}
    return {'chromium':{**common,'allowed_origins':['chrome-extension://'+chromium_id+'/']},
            'firefox':{**common,'allowed_extensions':[FIREFOX_ID]}}

def register(root):
    if os.name!='nt':raise ValueError('Windows шаардлагатай.')
    import winreg
    root=Path(root).resolve()
    if not (root/'RAINY.Native.exe').is_file():raise ValueError('Суулгасан RAINY.Native.exe олдсонгүй. Setup хувилбар шаардлагатай.')
    configs=manifests(root)
    # Host JSON lives in per-user app data, not Program Files.
    from host.runtime import DATA
    folder=DATA.parent/'browser-hosts';folder.mkdir(parents=True,exist_ok=True)
    paths={}
    for kind,m in configs.items():
        p=folder/(kind+'.json');p.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8');paths[kind]=str(p)
    for name,key in REGISTRY.items():
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER,key) as k:winreg.SetValueEx(k,'',0,winreg.REG_SZ,paths['firefox' if name=='Firefox' else 'chromium'])
    return list(REGISTRY)

def unregister():
    if os.name!='nt':return
    import winreg
    from host.runtime import DATA
    owned=str(DATA.parent/'browser-hosts')
    for key in REGISTRY.values():
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,key) as k:value=winreg.QueryValueEx(k,'')[0]
            if str(value).startswith(owned+os.sep):winreg.DeleteKey(winreg.HKEY_CURRENT_USER,key)
        except FileNotFoundError:pass

def status():
    result=[]
    for browser,key in REGISTRY.items():
        registered=False
        if os.name=='nt':
            import winreg
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER,key) as k:path=winreg.QueryValueEx(k,'')[0]
                m=json.loads(Path(path).read_text(encoding='utf-8-sig'));registered=Path(m['path']).is_file()
            except (OSError,ValueError,KeyError):pass
        result.append({'name':browser,'registered':registered,'extension_confirmed':False})
    return result
