from urllib.parse import urlsplit

def download_error(url,details):
    text=str(details or '');low=text.lower();host=(urlsplit(url).hostname or '').lower()
    if host=='facebook.com' or host.endswith('.facebook.com') or host=='fb.watch':
        if any(v in low for v in ['login','log in','registered users','private video','cookies']):
            message='Facebook энэ бичлэгт нэвтрэх эрх шаардаж байна. Нийтэд нээлттэй видеоны шууд холбоос ашиглана уу. Нэвтрэх эрхийн хамгаалалтыг тойрохгүй.'
        elif 'unsupported url' in low:
            message='Facebook-ийн тухайн Reel/видеог тусад нь нээгээд шууд холбоосыг оруулна уу. Feed/Page холбоосыг татах боломжгүй байж болно.'
        elif any(v in low for v in ['cannot parse','unable to extract','no video formats']):
            message='Facebook-ийн видео мэдээллийг хөдөлгүүр тайлж чадсангүй. Тухайн видео холбоос болон алдааны мэдээллийг хуулж илгээнэ үү.'
        elif 'requested format' in low:
            message='Facebook видеод сонгосон формат олдсонгүй. Доогуур чанар эсвэл MP3 сонгож үзнэ үү.'
        else:message='Facebook таталт амжилтгүй. Бичлэгийн шууд холбоос, сүлжээ болон хандалтыг шалгана уу.'
    else:message='Таталт амжилтгүй. Холбоос, сүлжээ болон видеоны хандалтыг шалгана уу.'
    return message+('\nДэлгэрэнгүй: '+text[-1000:] if text else '')
