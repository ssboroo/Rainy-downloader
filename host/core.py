"""Validated downloader arguments. No shell interpolation."""
import ipaddress
from urllib.parse import urlsplit, urlunsplit

def normalize_url(value):
    if not isinstance(value,str) or len(value)>4096: raise ValueError('Холбоос буруу байна.')
    value=value.strip()
    if any(ord(c)<32 for c in value): raise ValueError('Холбоос буруу байна.')
    try:
        p=urlsplit(value); host=(p.hostname or '').lower(); port=p.port
    except ValueError: raise ValueError('Холбоос буруу байна.')
    if p.scheme not in ('https','http') or not host or p.username or p.password or port not in (None,80,443):
        raise ValueError('Зөв HTTP/HTTPS холбоос оруулна уу.')
    if host=='localhost' or '.' not in host or host.endswith(('.local','.test','.internal')):
        raise ValueError('Нийтийн видео холбоос оруулна уу.')
    try:
        addr=ipaddress.ip_address(host)
        if not addr.is_global: raise ValueError('Дотоод хаягийг дэмжихгүй.')
    except ValueError as e:
        if 'Дотоод' in str(e): raise
    return urlunsplit((p.scheme,p.netloc,p.path,p.query,''))

def build_args(job,tools):
    url=normalize_url(job['url'])
    quality=int(job.get('quality',1080))
    if quality not in (360,480,720,1080,1440,2160): raise ValueError('Чанарын сонголт буруу.')
    fmt=job.get('format','mp4')
    if fmt not in ('mp4','mp3'): raise ValueError('Формат буруу.')
    args=[*tools['yt_dlp'],'--ignore-config','--encoding','utf-8','--no-playlist','--no-colors','--newline','--progress','--retries','3','--fragment-retries','3','--socket-timeout','20',
          '--windows-filenames','--trim-filenames','180','--no-overwrites','--paths',job['folder'],
          '--output','%(title).150B [%(id)s].%(ext)s',
          '--progress-template','download:RAINY_PROGRESS:%(progress)j',
          '--print','after_move:RAINY_FILE:%(filepath)s']
    if fmt=='mp3': args+=['--extract-audio','--audio-format','mp3','--audio-quality','192K']
    else:
        args+=['--format',f'bv[ext=mp4][vcodec^=avc1][height<={quality}]+ba[ext=m4a]/b[ext=mp4][height<={quality}]','--merge-output-format','mp4']
    return args+['--',url]
