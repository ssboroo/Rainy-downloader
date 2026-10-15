# Windows release шалгалт · 2026-10-15

## Амжилттай Windows build

Release: v2.0.0-build.5. Code commit: 3c0f300a870b4df59e09cc32b6c6fe88b7ab9860.

Run: https://github.com/ssboroo/Rainy-downloader/actions/runs/38706831354

- Windows x64 runner, Python 3.12.
- 39 Python болон 8 JavaScript тест амжилттай.
- GUI болон console Native Messaging executable build амжилттай.
- Upstream release SHA256-тай шалгасан yt-dlp/FFmpeg/ffprobe/Deno багцлагдсан.
- Packaged tool version/health probes амжилттай.
- yt-dlp binary дутуу үед health fail болж, давхар GUI spawn үлдээгээгүй.
- Packaged Native Messaging roundtrip: PASS.
- Packaged desktop window launch: PASS — жинхэнэ Windows процессоор GUI нээж, UIA-аар харагдах цонхыг илрүүлсэн.
- Inno Setup installer build, artifact upload, public release publication амжилттай.

## Туршаагүй, хязгаар

- Installer-ийг хэрэглэгчийн Windows дээр суулгах/устгах бүрэн flow.
- Браузер бүрийн бодит хаягийн мөрийг UIA-аар capture хийх болон floating control focus/menu lifecycle.
- Бодит YouTube/Facebook/Instagram/X/TikTok болон бусад сайтын таталт, MP4/MP3 хөрвүүлэлт.
- Firefox signing, Chrome/Edge store publication болон code-signing. Installer unsigned.

Хөвөгч товч нь OS-level control; website injection эсвэл видео бүрийг илрүүлэх систем биш. Browser process whitelist нь Chrome, Edge, Brave, Opera, Firefox, Vivaldi. Хаягийн мөр танихгүй бол гараар холбоос оруулна. Document ancestry-тай webpage input-уудыг уншиж хаяг гэж авахгүй.

## Шалтгаан ба засварын бүртгэл

- Хэрэглэгчийн Windows логийн UTF8/cp1252, SQLite WinError32, short/long canonical path, Python3.14 auto selection алдаануудыг зассан; бодит Windows suite дараа нь амжилттай болсон.
- Frozen tools дутуу үед GUI fallback spawn хийх, ambiguous feed link, async submission gate болон UI-thread SQLite contention-ийн regression тестүүд орсон.
- Анхны floating build нь unauthenticated GitHub API rate limit-д зогссон. Actions-ийн өөрийн token-ыг зөвхөн api.github.com metadata хүсэлтэд ашиглахаар зассан; дараагийн build амжилттай.
- Тусдаа reviewer UIA field capture-ийн чухал алдааг олж, browser-native toolbar/control ID болон Document ancestry exclusion-оор зассан.
