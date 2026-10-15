# RAINY Татагч Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development to implement task-by-task. Steps use checkbox syntax.

**Goal:** Монгол интерфэйстэй Windows Chrome видео татагчийг суулгах боломжтой эх кодын ZIP багцаар хүргэх.

**Architecture:** Manifest V3 өргөтгөл Native Messaging-ээр Python туслах програмтай холбогдоно. Туслах програм yt-dlp, FFmpeg, Deno ашиглаж таталт болон дискэнд хадгалах дарааллыг удирдана. Өргөтгөлийн цонхоос үл хамааран үргэлжлэх worker нь хэрэглэгчийн Windows session-д ажиллана.

**Tech Stack:** JavaScript, HTML/CSS, Python 3.11+, PowerShell, yt-dlp, FFmpeg, Deno; Python unittest, Node built-in test.

**Spec:** [RAINY-Downloader-Design-MN.md](RAINY-Downloader-Design-MN.md)

## Global Constraints
- Windows 10/11, Chrome Manifest V3; хэрэглэгчид харагдах бүх текст монгол хэлтэй.
- Нэгэн зэрэг нэг таталт; хэрэглэгчийн үйлдлээр дараалалд нэмнэ.
- Нууц үг, cookie автоматаар уншихгүй; DRM хамгаалалтыг тойрохгүй.
- Бүх сайт, бүх видеог татна гэсэн амлалт өгөхгүй.
- Shell мөрөөр команд ажиллуулахгүй; Native host зөвшөөрөгдсөн extension ID-г шалгана.
- Windows дээр туршаагүй зүйлсийг хүргэлтийн тайланд тэмдэглэнэ.

## Review Focus
- Эвдэрсэн Native Messaging frame болон хэт том мессеж процесс унагаахгүй.
- Хавтас, нэрэнд монгол үсэг болон зай байхад аргумент эвдрэхгүй.
- Playlist холбоос хэрэглэгчийн сонголтгүйгээр бүхэлд нь татагдахгүй.
- Popup хаагдах, Chrome дахин нээгдэхэд төлөв алдагдахгүй.
- FFmpeg, Deno, yt-dlp байхгүй үед монгол тайлбар гарна.

## Task 1: Core validation and persistent queue
**Files:** `host/core.py`, `host/storage.py`, `tests/test_core.py`, `tests/test_storage.py`.
**Interfaces:** `normalize_url(value: str) -> str`; `build_args(job: dict, tools: dict) -> list[str]`; `Store(path).enqueue(job: dict) -> dict`, `.snapshot() -> dict`, `.update(id: str, fields: dict) -> None`.
- [ ] Write failing tests: reject file/javascript URLs, deceptive domains; preserve Unicode path as one argument; enforce no-playlist default; reject duplicate active URLs; preserve jobs across Store reload; mark interrupted jobs recoverable.
- [ ] Run `python -m unittest discover -s tests -v`; confirm missing implementation failures.
- [ ] Implement SQLite-backed queue, URL validation, MP4-compatible selection, MP3 conversion arguments, job state transitions and output path constraints.
- [ ] Re-run tests; require all pass. Commit task.

## Task 2: Native host and independent download worker
**Files:** `host/native.py`, `host/worker.py`, `host/protocol.py`, `tests/test_protocol.py`, `tests/test_worker.py`.
**Interfaces:** messages `{id, action, payload}` return `{id, ok, data, error}`. Actions `health`, `inspect`, `enqueue`, `snapshot`, `cancel`, `settings`, `open_folder`. Worker consumes Task 1 Store; `read_frame(stream) -> dict | None`; `write_frame(stream, message: dict) -> None`.
- [ ] Write failing tests: truncated/oversize frame rejected, stdout framing preserved, missing executables reported, inspection timeout terminates process, cancellation stops owned process tree, playlist inspection returns count and entries for explicit selection.
- [ ] Run unittest suite and confirm failures.
- [ ] Implement stdio framing with 1 MiB limit, health dependency probes, yt-dlp JSON inspection, background worker startup with singleton lock, bounded retry, progress parsing, SQLite status updates, cancellation and path-restricted folder opening. Child process output never pollutes protocol stdout.
- [ ] Run suite; require all pass. Commit task.

## Task 3: Mongolian Chrome interface
**Files:** `extension/manifest.json`, `extension/background.js`, `extension/popup.html`, `extension/popup.js`, `extension/styles.css`, `extension/options.html`, `extension/options.js`, `extension/shared.js`, `tests/extension.test.mjs`.
**Interfaces:** `request(action, payload) -> Promise<data>` consumes Task 2 messages. UI displays job fields `id,url,title,status,progress,speed,eta,error,output_path`; settings `folder,format,quality,oneClick`.
- [ ] Write failing Node tests for URL normalization, setting defaults, quality value validation, error-to-Mongolian mapping, formatted progress and escaped DOM text handling.
- [ ] Run `node --test tests/extension.test.mjs`; confirm failure.
- [ ] Implement light blue UI, accessible controls, active-tab URL capture, inspect/results flow, MP4/MP3 and quality choices, batch links, explicit playlist selection, queue/history, cancel, folder opening, settings persistence and opt-in one-click mode. Use textContent for external metadata. Poll snapshots only while UI visible; background worker owns downloads.
- [ ] Run Node/Python suites and JavaScript syntax checks; inspect popup rendered in available browser, record if Chrome extension integration cannot be tested. Commit task.

## Task 4: Windows installation and deliverable
**Files:** `windows/install.ps1`, `windows/uninstall.ps1`, `windows/start-host.cmd`, `README-MN.md`, `THIRD-PARTY-NOTICES.md`, `VALIDATION.md`, `scripts/package.py`.
**Interfaces:** installer accepts `-ExtensionId` matching `[a-p]{32}`, creates per-user NativeMessagingHosts registration and isolated Python environment, writes allowed_origins with exact extension ID; uninstall removes only app-owned files/registry entries.
- [ ] Add tests for generated native manifest, extension ID rejection, archive contents and dependency detection failures. Run and confirm failure.
- [ ] Implement idempotent dependency checks and install steps using official sources, display dependency versions, validate installation before success. Do not change global execution policy. Document Python/FFmpeg/Deno installation requirements and licenses; stop with actionable instructions when downloads are blocked.
- [ ] Write Mongolian installation, use, troubleshooting and uninstall instructions. State public-content scope and platform support limits. Package source and installers into `RAINY-Downloader-Windows.zip`.
- [ ] Run all automated checks, parse manifest, compile Python, inspect archive listing. Record Windows/manual site checks as performed or unperformed without implying success.
- [ ] Review against approved spec; fix material gaps, commit, save ZIP and validation report, provide links.

## Execution selection
Recommend native execution in this session: the four tasks share the same message protocol and queue model, so keeping implementation together reduces interface drift. The user reviews this plan before implementation begins.
