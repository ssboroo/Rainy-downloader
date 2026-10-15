# Шалгалтын тайлан · 2026-10-15

## Баталгаажуулсан хүрээ

- Python unittest: 24 тест. Холбоос/аргумент, Unicode зам, SQLite түүх ба давхардал, цуцлалтын төлөв, 200-аас олон ажлын хяналт, snapshot хэмжээ, гүн/дутуу/буруу UTF-8 Native Messaging frame, тогтмол extension ID, playlist мэдээлэл.
- Native host-ыг тусдаа Python процессоор ажиллуулж зөв origin-оос framed snapshot авсан; буруу origin-оос гаралт өгөөгүй.
- Worker-ыг бодит туслах тест процессоор ажиллуулж progress/file output уншсан, Unicode нэртэй тест файл үүсгэсэн; тусдаа ажиллаж буй тест процессыг цуцалж зогсоосон. Эдгээр нь жинхэнэ видео таталт биш.
- Node built-in tests: 3 тест. UI URL шалгалт, тохиргоо/хувь, Native Messaging алдааг монголоор харуулах.
- JavaScript syntax, Python compile, manifest JSON, icons болон ZIP бүтцийг шалгана.
- Тусдаа code review хийгдсэн. Олдсон дөрвөн чухал алдаа: 200 ажлын дараах lookup, цуцлалтын race, 1 MiB-ээс том snapshot, гүн JSON. Дахин үүсгэх тестүүдээр эхлээд алдааг нотлоод зассан.

## Туршаагүй зүйлс

- Windows 10/11 дээр PowerShell installer, registry, .cmd native host launcher болон жинхэнэ Chrome extension хоорондын end-to-end холболт. Энэ орчин Linux.
- YouTube, Facebook, Instagram, X, TikTok болон бусад сайтын жинхэнэ видео таталт.
- Бодит MP4 нэгтгэл, MP3 хөрвүүлэлт болон Chrome хаасан үеийн бодит Windows worker ажиллагаа.
- Browser visual / popup interaction QA. Playwright browser суулгах оролдлого бүтэлгүйтсэн тул render болон click-through хийгдээгүй. Интерфэйсийн код байгаа ч screenshot-based QA хийгдээгүй.
- Windows хэрэглэгчийн нэр нь монгол үсэг, зай агуулсан бодит суулгалт. Python талын Unicode/spaced path тест хийгдсэн.

Иймээс энэ хүргэлт нь суулгаж турших эхний ажиллах зориулалттай эх кодын багц; бүх платформ дээр production-ready гэдгийг баталсан release биш.

## Хяналтаас үлдсэн жижиг зүйлс

- Playlist-ийн count нь шалгасан эхний 100 хүртэл бичлэгийн тоо; бүх playlist-ийн нийт тоо гэж ойлгохгүй. Зааварт энэ хязгаарыг тэмдэглэсэн.
- Health нь executable PATH-д байгаа эсэх, yt-dlp package хувилбарыг шалгана. FFmpeg/ffprobe/Deno executable бүрийг version командтай ажиллуулж эвдрээгүйг нотлох нэмэлт probe хийгдээгүй.
- Full browser/Windows integration тестүүдийг дээр дурдсан орчинд гүйцээх шаардлагатай.

## Хэрэгжүүлэлтийн шийдвэрүүд

- Шинэ, хоосон workspace-д тусдаа feature branch үүсгэсэн; хэрэглэгчийн өмнөх repository өөрчлөөгүй.
- Гуравдагч програмын unsigned бинарийг ZIP-д оруулаагүй. Суулгац албан ёсны багцын сангаас авна; анхны суулгалт интернэт шаарддаг.
- Manifest public key ашиглан unpacked extension ID-г тогтмол болгосон. Хувийн signing key хүргэхгүй. Key-г өөрчилбөл installer-ийн ID-г тохируулах шаардлагатай.
- Түүхийг дэлгэц дээр хэмжээгээр хязгаарладаг; бүх ажлыг SQLite-д хадгалж, worker/cancel/recovery нь display limit-ээс үл хамааран ажиллана.
