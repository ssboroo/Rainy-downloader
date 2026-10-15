# RAINY Desktop + браузерын холболт

Хэрэглэгчийн баталсан хүрээ: Windows програм суулгах; браузер бүрт нэг удаа өргөтгөлийг зөвшөөрсний дараа видео дээр татах товч харагдах. Браузерын хамгаалалтыг тойрч өргөтгөл чимээгүй суулгахгүй.

Windows desktop UI нь одоогийн SQLite queue, worker, yt-dlp аргументуудыг дахин ашиглана. CustomTkinter light UI; background thread нь шалгалт, таталтын хүсэлт гүйцэтгэнэ. Tk widget зөвхөн UI thread дээр өөрчлөгдөнө. UI хаагдсан ч worker тусдаа процесс тул үргэлжилнэ.

Браузер content script нь HTML video element-ийн ойролцоо товч гаргана. YouTube/Facebook/Instagram/X/TikTok-ийн нийтлэлийн холбоосыг page/card context-оос авна; blob холбоос дамжуулахгүй. Олон посттой feed-д тухайн видеоны permalink олдохгүй бол таталт эхлүүлэхгүй, тухайн постыг тусад нь нээх зөвлөгөө харуулна. Ерөнхий сайтын шууд HTTP media URL эсвэл single-video page URL-г хэрэглэнэ. Closed shadow DOM, canvas player, зарим iframe-г 100% дэмжихгүй.

Товч нь жижиг сонголт (MP4/MP3, чанар) харуулж, дараалалд нэмэхэд Native Messaging ашиглана. Public web page нь Native Messaging action-уудыг шууд дуудахгүй; extension background content sender-оос зөвхөн video enqueue зөвшөөрнө. Browser integration optional permissions нь хэрэглэгчийн сонголтоор асаагдана; суулгах үед бүх сайтын access-ыг нууцаар олгохгүй.

Chrome/Edge/Brave/Opera-д Chromium helper. Firefox build тусдаа stable Gecko ID, native allowed_extensions ашиглана. Тогтвортой Firefox-д signed XPI шаардлагатай. Chromium дэлгүүрүүдэд нийтлэх болон signing нь дараагийн түгээлтийн шат; энэ ажилд нийтлэхгүй.

Windows release нь GUI executable, console native host, тусдаа yt-dlp/FFmpeg/ffprobe/Deno tools бүхий Inno Setup installer. Хэрэглэгчид Python суулгах шаардлагагүй. Windows CI build script болон workflow бэлдэнэ. Windows runner байхгүй бол жинхэнэ Setup.exe үүссэн гэж мэдэгдэхгүй.
