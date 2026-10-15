# RAINY Татагч · Windows

Монгол интерфэйстэй Windows видео/аудио татагч. Өргөтгөлгүй Windows хөвөгч товч болон нэмэлт браузерын helper-тэй.

**[RAINY-Setup.exe татах · хамгийн сүүлийн хувилбар](https://github.com/ssboroo/Rainy-downloader/releases/latest/download/RAINY-Setup.exe)**

[Release](https://github.com/ssboroo/Rainy-downloader/releases/latest) · [Амжилттай Windows build](https://github.com/ssboroo/Rainy-downloader/actions/runs/38711015492)

## Суулгах ба ашиглах

1. RAINY-Setup.exe татаж суулгана. Хэрэглэгч Python, Node эсвэл build хэрэгсэл суулгах шаардлагагүй.
2. Desktop-ийн RAINY Татагч дүрсээр програмыг нээнэ.
3. Дэмжигдэх браузер идэвхтэй үед дэлгэцийн баруун талын **↓ RAINY · Татах** хөвөгч товчийг дарна.
4. Програм браузерын хаягийн мөрийг Windows UI Automation-оор уншиж, холбоосыг шалган таталтын дараалалд нэмнэ. Хаягийг найдвартай танихгүй үед холбоосоо програмд оруулж болно.

Энэ хөвөгч товч нь веб хуудсанд суулгасан control биш. Видео бүрийг автоматаар танихгүй; feed дээр тухайн видео нийтлэлийг тусад нь нээнэ. Chrome, Edge, Brave, Opera, Firefox, Vivaldi process detection орсон; браузер бүрийн хэл/хувилбар/accessibility тохиргооны нийцэл тусдаа шалгалт шаарддаг.

Гол цонхны X нь програмыг нууж хөвөгч control-ыг ажиллуулж үлдээнэ. Хөвөгч товч дээр баруун дарж програмыг нээх эсвэл бүрэн гарна. Installer-ийн Windows нэвтрэхэд эхлүүлэх сонголт optional.

## Боломж

- Монгол хэл, цайвар desktop UI.
- MP4 / MP3, боломжит дээд чанар, хавтас сонголт.
- Автомат таталтын дараалал, явц/хурд, цуцлах, дахин татах, түүх.
- Олон холбоос, playlist-ийн сонголт.
- Өргөтгөлгүй хөвөгч Windows control; page доторх товчийн optional helper тусдаа.
- Нууц үг/clipboard-ыг background-д уншихгүй; веб Document доторх input-ыг браузерын хаяг гэж авахгүй.

## Шалгасан хүрээ

Windows CI: 43 Python + 9 Node tests, packaged dependency health, missing-tool failure, native host roundtrip, packaged GUI window launch, Inno Setup build амжилттай. Silent installer install/uninstall, браузер бүрийн бодит UIA, бодит сайтын видео таталт болон SmartScreen/code-signing шалгалт хийгдээгүй. Installer unsigned.

[Дэлгэрэнгүй заавар](README-DESKTOP-MN.md) · [Шалгалтын тайлан](VALIDATION-DESKTOP.md) · [Dependencies](THIRD-PARTY-NOTICES.md)
