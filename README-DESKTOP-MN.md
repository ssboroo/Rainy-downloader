# RAINY Desktop · Windows татагч

## Өргөтгөлгүй ашиглах

Шинэ хувилбарт браузерын өргөтгөл шаардлагагүй **Windows хөвөгч товч** бий. Програм ажиллаж байх үед Chrome, Edge, Brave, Opera, Firefox, Vivaldi-ийн идэвхтэй цонх танигдвал дэлгэцийн баруун талд **↓ RAINY · Татах** товч харагдана.

Товчийг дарахад Windows UI Automation-оор тухайн браузерын хаягийн мөрийг уншиж, холбоосыг RAINY-д шалган таталт эхлүүлнэ. Хаягийн мөрийг найдвартай уншиж чадахгүй бол гараар холбоос оруулах зөвлөгөө гарна. Clipboard, нууц үг болон page content-ыг background-д уншихгүй.

Энэ нь веб хуудас дотор суулгасан товч биш, Windows-ийн тусдаа хөвөгч control. Браузер байгааг танихаас видео бүрийг танихгүй. Feed-ийн нэг постыг тусад нь нээж ашиглана. Зарим браузер/хэл/accessibility тохиргоонд UI Automation ажиллахгүй байж болно.

Хөвөгч товч дээр баруун товч → **RAINY програм нээх** эсвэл **Програмаас гарах**. Гол цонхны X нь програмыг нууж, хөвөгч control-ыг ажиллуулж үлдээнэ. Installer-д Windows нэвтрэхэд эхлүүлэх optional сонголт бий.

Хуудас доторх per-video товч хүсвэл доорх optional browser helper ашиглана. Chrome/Firefox-ийн хамгаалалтыг тойрч чимээгүй extension суулгахгүй.

---

# Build болон нэмэлт браузерын helper-ийн заавар

## Энэ багцын төлөв

Энэ нь desktop програм, браузерын өргөтгөлүүд болон Windows installer build-ийн **эх кодын багц**. Эх кодын хавтсанд Setup.exe орохгүй. Бэлэн installer-ийг GitHub Releases-ээс татна: https://github.com/ssboroo/Rainy-downloader/releases/tag/v2.0.0-build.5 . Windows build болон packaged GUI/native smoke шалгалт амжилттай дууссан.

## Бэлэн installer гарсны дараах хэрэглэгчийн урсгал

1. **RAINY-Setup.exe**-г ажиллуулна. Desktop shortcut болон Windows Start menu үүснэ. Эцсийн хэрэглэгчид Python суулгах шаардлагагүй байхаар build хийгдэнэ; таталтын хэрэгслүүд багцлагдана.
2. RAINY → **Браузерын холболт** хэсгийг нээнэ.
3. Native host бүртгэл нь Chrome, Edge, Brave, Opera, Firefox-т үүснэ. Host бүртгэл байгаа нь extension асаалттай гэсэн баталгаа биш.
4. Браузерын helper-ийг нэг удаа өөрөө зөвшөөрнө. Одоогийн development хувилбарт Chromium браузерын Extensions → Developer mode → Load unpacked → програмын `browser-extensions/chromium` хавтсыг сонгоно.
5. Helper-ийн ⚙ → **Сайтууд дээр товч гаргахыг зөвшөөрөх** дарж хуудасны хандалтыг зөвшөөрнө.
6. Видео хуудсаа refresh хийнэ. Танигдсан HTML video-ийн ойролцоо **↓ Татах** товч гарна.
7. Товч → MP4/MP3, дээд чанар → **Дараалалд нэмэх**. RAINY програмын **Таталтууд** хэсгээс явцыг харна.

Өргөтгөлийг browser store-д нийтлэх/sign хийх шат энэ багцад хийгдээгүй. Chrome/Edge/Brave/Opera-ийн бодит хувилбар бүрд end-to-end туршилт шаардлагатай. Тогтвортой Firefox хэрэглэгчид Mozilla-аар signed XPI хэрэгтэй; `firefox-development.zip` нь signed installer биш. Хөгжүүлэгчийн түр туршилтад about:debugging ашиглана.

## Desktop програмын боломж

- Монгол хэлтэй цайвар интерфэйс, sidebar, таталтын картууд.
- Холбоосоор шалгаж татах, MP4/MP3, чанар сонгох.
- Хавтас сонгох стандарт Windows dialog.
- Нэг мөрөнд нэг холбоосоор 100 хүртэл холбоос нэмэх.
- Playlist-ийн эхний 100 хүртэл бичлэгээс гараар сонгох.
- Автомат дараалал, таталтын хувь/хурд/хугацаа, цуцлах, дахин татах, хавтас нээх.
- Worker нь тусдаа процесс тул GUI хаагдсан үед таталт үргэлжилж болно. Компьютер унтрах, хандалт цуцлагдах зэрэгт үргэлжилнэ гэсэн баталгаа өгөхгүй.
- Browser host-ийн бүртгэл болон external tools-ийн version commands-ыг шалгах health.

## Браузер дахь товчийн хязгаар

YouTube/Facebook/Instagram/X/TikTok-ийн тухайн видео постын permalink-г танихыг оролдоно. Олон посттой feed дээр холбоос нь тодорхойгүй бол дурын постыг тааж татахгүй; постыг тусад нь нээхийг зөвлөнө. Generic HTML video-д шууд HTTP медиа холбоос эсвэл нэг видеотой хуудсыг ашиглана. `blob:` холбоосыг шууд татахад дамжуулахгүй.

Closed shadow DOM, canvas player, fullscreen, зарим iframe, нэвтрэх шаардлагатай пост болон сайтыг бүхэлд нь 100% дэмжихгүй. DRM хамгаалалтыг тойрохгүй. Нууц үг/cookie автоматаар уншихгүй. Товчийг ажиллуулах site access нь optional бөгөөд хэрэглэгч өөрөө зөвшөөрнө.

## Windows дээр installer build хийх

Шаардлага: Windows x64, Python 3.12, Node.js 22+, Inno Setup 6, интернэт. Эдгээр нь **build хийж буй хөгжүүлэгчид** хэрэгтэй; гарсан installer-ийн хэрэглэгчид Python/Node хэрэггүй.

1. Эх кодын ZIP-ийг бүрэн задлах.
2. **BUILD-WINDOWS.cmd** ажиллуулах.
3. Скрипт build Python орчин бэлдэж, тестүүд ажиллуулж, GUI EXE болон console Native Messaging EXE үүсгэнэ.
4. yt-dlp, Deno, FFmpeg/ffprobe-г upstream GitHub releases-ээс татаж, GitHub-ийн SHA256 digest-тай тулгана. Digest олдохгүй бол шалгалтыг алгасахгүй, build зогсоно.
5. Packaged tools-ийн version probes болон Native Messaging roundtrip-ыг ажиллуулна.
6. Inno Setup installer гаргана: **release/RAINY-Setup.exe**.

Хэрэв Inno Setup байхгүй бол албан ёсны installer суулгана: `winget install JRSoftware.InnoSetup`. Node/Python хэрэгтэй бол албан ёсны хувилбарыг суулгана.

Installer нь unsigned тул Windows SmartScreen нэр хүнд/гарын үсгийн мэдэгдэл харуулж болно. Гарын үсэг зурах сертификат болон дэлгүүрийн нийтлэл энэ ажилд ороогүй.

## GitHub Actions-оор build хийх

Эх кодыг зориулалтын GitHub repository-д оруулна. **Actions → Build Windows installer → Run workflow** ажиллуулна. Амжилттай бол **RAINY-Windows-Setup** artifact дотор Setup.exe болон dependency versions/health report байна. Workflow repository руу өөрчлөлт push хийх эрхгүй; зөвхөн build artifact гаргана.

Windows build ажиллуулаагүй үед artifact байна гэж үзэхгүй. CI build амжилттай байсан ч browser integration болон бодит сайтуудын гар туршилт дараагийн шалгалт хэвээр.

## Source байдлаар хөгжүүлэх

```powershell
python -m pip install -r requirements-desktop.txt "yt-dlp[default]"
python -m desktop.entry
```

FFmpeg, ffprobe, Deno PATH-д байх ёстой. Source UI ажилласан ч packaged native bridge байхгүй бол шинэ browser-host register товч зөвхөн Setup build шаардлагатай гэсэн тайлбар өгнө. Хуучин Python native setup нь тусдаа development урсгал бөгөөд installer-тэй андуурч болохгүй.

## Өгөгдөл, устгах

Түүх, тохиргоо: `%LOCALAPPDATA%\RAINYDownloader\data`.

Desktop installer-ийн програм: `%LOCALAPPDATA%\Programs\RAINY`.

Татсан видео хэрэглэгчийн сонгосон хавтсанд хадгалагдана. RAINY server рүү бичлэг дамжуулахгүй. App uninstaller нь app-owned Native Messaging бүртгэлийг цэвэрлэхээр хийгдсэн; browser helper-ээ браузераас Remove хийнэ. Таталт ажиллаж байхад update/uninstall хийхийн өмнө цуцлах эсвэл дуусгах шаардлагатай.

Баталгаажуулсан болон туршаагүй хэсгийг **VALIDATION-DESKTOP.md**-ээс харна уу. Хуучин README-MN.md нь өмнөх Python extension helper урсгалын заавар.

## Windows build-ийн засвар — 2026-10-15

Windows дээрх cp1252 UnicodeDecodeError, SQLite WinError 32, богино/бүтэн замын тест болон child stdout encoding алдааг зассан. Шинэ багцыг **шинэ хавтсанд** задлаад BUILD-WINDOWS.cmd ажиллуулна. Өмнөх .build-venv нь Python 3.14-тэй байж болох тул хуучин орчныг шинэ багц руу хуулж болохгүй.

Build нь `py -3.12` ашиглана. Python 3.12 байхгүй бол `winget install --exact --id Python.Python.3.12` ажиллуулж терминалаа шинээр нээнэ. 3.14-ийг заавал устгах шаардлагагүй.
