"""Explicit, read-only address-bar capture. No keyboard interception or clipboard access."""
import os,ctypes
from pathlib import PureWindowsPath
from host.core import normalize_url
BROWSERS={'chrome.exe','msedge.exe','brave.exe','opera.exe','firefox.exe','vivaldi.exe'}
def is_browser_executable(value):return PureWindowsPath(str(value)).name.lower() in BROWSERS

def address_url(value):
    value=str(value).strip()
    if any(c.isspace() for c in value):raise ValueError('Хаягийн мөрөөс видео холбоос олдсонгүй.')
    if '://' not in value:value='https://'+value
    return normalize_url(value)

def foreground_browser():
    if os.name!='nt':return None
    from ctypes import wintypes
    user=ctypes.windll.user32;kernel=ctypes.windll.kernel32
    user.GetForegroundWindow.restype=wintypes.HWND
    user.GetWindowThreadProcessId.argtypes=[wintypes.HWND,ctypes.POINTER(wintypes.DWORD)]
    hwnd=user.GetForegroundWindow()
    if not hwnd:return None
    pid=wintypes.DWORD();user.GetWindowThreadProcessId(hwnd,ctypes.byref(pid))
    kernel.OpenProcess.restype=wintypes.HANDLE;kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD]
    kernel.QueryFullProcessImageNameW.argtypes=[wintypes.HANDLE,wintypes.DWORD,wintypes.LPWSTR,ctypes.POINTER(wintypes.DWORD)]
    kernel.CloseHandle.argtypes=[wintypes.HANDLE]
    process=kernel.OpenProcess(0x1000,False,pid.value)
    if not process:return None
    try:
        text=ctypes.create_unicode_buffer(32768);size=wintypes.DWORD(len(text))
        if not kernel.QueryFullProcessImageNameW(process,0,text,ctypes.byref(size)):return None
        if not is_browser_executable(text.value):return None
        return {'handle':int(hwnd),'browser':PureWindowsPath(text.value).stem,'pid':pid.value}
    finally:kernel.CloseHandle(process)

def trusted_address_control(name,automation_id,ancestor_types):
    if not ancestor_types or 'Document' in ancestor_types:return False
    auto=str(automation_id).lower()
    known=auto in {'addresseditbox','urlbar-input','omnibox','omniboxview','urlbar'}
    named=any(part in str(name).lower() for part in ['address','omnibox','urlbar','location','хаяг'])
    return 'Window' in ancestor_types and (known or ('ToolBar' in ancestor_types and named))

def capture_address(handle):
    if os.name!='nt':raise ValueError('Браузер таних үйлдэл Windows-д зориулагдсан.')
    # COM/UIAutomation objects are created and released on the worker thread.
    import pythoncom
    pythoncom.CoInitialize()
    try:
        from pywinauto import Desktop
        window=Desktop(backend='uia').window(handle=int(handle))
        candidates=[]
        for edit in window.descendants(control_type='Edit'):
            name=(edit.element_info.name or '').lower();auto=(edit.element_info.automation_id or '').lower()
            ancestors=[];node=edit
            try:
                for _ in range(40):
                    node=node.parent();kind=node.element_info.control_type;ancestors.append(kind)
                    if kind=='Document':break
                    if kind=='Window' and int(node.handle or 0)==int(handle):break
                else:continue
            except Exception:continue
            if not trusted_address_control(name,auto,ancestors):continue
            try:value=edit.get_value()
            except Exception:continue
            try:candidates.append(address_url(value))
            except ValueError:continue
        candidates=list(dict.fromkeys(candidates))
        if len(candidates)!=1:raise ValueError('Браузерын хаягийг найдвартай таньсангүй. Холбоосоо RAINY програмд хуулж оруулна уу.')
        return candidates[0]
    finally:pythoncom.CoUninitialize()
