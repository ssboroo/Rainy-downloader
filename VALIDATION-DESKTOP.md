# Desktop 2 шалгалт · 2026-10-15

## Хийгдсэн

- Python suite: 35 тест; шинэ runtime source/frozen command, external binary lookup, per-browser manifests, desktop controller queue/settings/cancel, Chromium/Firefox helper outputs.
- JavaScript suite: 8 тест; платформын video permalink, blob/feed ambiguity, inline payload validation, extension tab vs web content sender.
- Өмнөх worker/process/protocol/queue regression тестүүд мөн ажилласан.
- Python compile, JavaScript syntax болон manifest/archive бүтцийн шалгалт.
- Official GitHub release metadata-г live шалгасан: yt-dlp.exe, Deno Windows ZIP, FFmpeg essentials ZIP нь одоогийн release дээр SHA256 digest-тай байв. Build script үүнийг татах бүрдээ дахин шалгана. Windows binary-уудыг энэ багцад татаж багцлаагүй.

## Одоогоор хийгдээгүй

- Windows PyInstaller, Inno Setup build; **RAINY-Setup.exe хараахан үүсээгүй**.
- Packaged tools/native smoke test нь Windows workflow-д бичигдсэн боловч энд ажиллаагүй.
- GUI-ийн бодит render/click-through болон Windows registry integration.
- Chrome/Edge/Brave/Opera/Firefox-ийн бодит video button injection.
- Сайт бүрийн бодит таталт, MP4/MP3 хөрвүүлэлт.
- Firefox signing болон browser store publication.

CustomTkinter 5.2.2 суулгаж, desktop.app module import амжилттай шалгасан; screenshot-based QA гэж үзэхгүй. Бодит desktop release гаргахад Windows build амжилттай дуусах, installer smoke test болон video/browser checks нэмэгдэх ёстой.

## Шийдвэрүүд

- Системийн траффик interception хийхийн оронд optional browser helper + Native Messaging сонгосон. Браузер бүрд нэг удаагийн зөвшөөрөл шаардлагатай.
- Windowed GUI EXE болон console Native EXE-г тусад нь build хийнэ. Native Messaging нь stdin/stdout binary handles шаарддаг тул windowed GUI exe-г шууд native host болгож болохгүй.
- Download engine-ийн binary-уудыг Windows build үед upstream source-оос SHA256 verification-тэй авна. Энэ source ZIP нь setup executable-ийг орлохгүй.
- Firefox хувилбар development helper бөгөөд signing хийгдээгүй. Chromium хөгжүүлэлтийн helper нь Load unpacked шаарддаг; чимээгүй browser policy суулгахгүй.

## Independent review ба засвар

Тусдаа reviewer source, browser, build урсгалыг хянасан. Чухал дөрвөн finding-ийг зассан:
- Frozen tool missing үед Python fallback хийж GUI spawn хийхгүй. Unit regression болон Windows CI-д renamed-tool health smoke test нэмсэн (Windows smoke хараахан ажиллаагүй).
- Нэг card-д хоёр өөр video permalink байвал дурын нэгийг сонгохгүй.
- Submission gate-ийг health/refresh completion суллахгүй.
- SQLite startup/settings/snapshot ажлууд UI thread-ээс тусдаа task runner дээр хийгдэнэ. Held writer lock-той үед result drain блоклохгүйг тестээр шалгасан. Бодит Tk heartbeat Windows дээр туршаагүй.

Нийт автомат тест: 43. Screenshot/UI, frozen exe, installer болон бодит browser/site шалгалтыг эдгээр тест орлохгүй.

## Windows build логийн дагуух засвар

Хэрэглэгчийн бодит Windows логт 1 failure, 11 error байсан. Шалтгаан: default cp1252 text I/O, SQLite context manager холболтыг хаадаггүйг тооцоогүй, Unicode child stdout, resolved Windows short/long path-ийн тест. Python 3.14 нь `py -3`-аар санамсаргүй сонгогдсон.

Засварын regression: холболт context-оос гарсны дараа retained reference байсан ч хаагдсаныг болон exception үед хаагдсаныг нотолсон; cp1252 file I/O нөхцөлийг дуурайлган browser build шалгасан. cp1252 child stdout-той integration suite-г тусад нь алдаатайг эхэлж нотлоод засварын дараа 5/5 болгосон. Нийт suite 35 Python + 8 Node тест амжилттай. Тусдаа reviewer материаллаг алдаа олоогүй.

Эдгээр нь Linux дээрх reproduction/regression шалгалтууд. Windows-ийн бүрэн build болон Setup.exe үүссэн гэж үзэхгүй; шинэ багцаар Windows build-ийг дахин ажиллуулах шаардлагатай.
