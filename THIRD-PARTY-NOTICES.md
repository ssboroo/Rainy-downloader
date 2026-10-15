# Dependencies and sources

This ZIP contains original RAINY source, not the third-party executables below. The installer obtains dependencies from their distribution channels. Actual Python package versions are recorded in installed-versions.txt after installation. A current yt-dlp release is installed rather than freezing a version that may lose site compatibility.

- Chrome Native Messaging documentation: https://developer.chrome.com/docs/extensions/develop/concepts/native-messaging
- yt-dlp: https://github.com/yt-dlp/yt-dlp — Unlicense for upstream source; dependency and bundled-distribution licenses vary. The installer uses the PyPI default extra including the current EJS dependency. Follow upstream licenses.
- yt-dlp EJS: https://github.com/yt-dlp/ejs — see repository license and runtime requirements.
- FFmpeg/ffprobe: https://ffmpeg.org/ — LGPL/GPL terms depend on the installed build. Gyan builds: https://www.gyan.dev/ffmpeg/builds/ . No FFmpeg binary is bundled here.
- Deno: https://github.com/denoland/deno — MIT; installed through winget DenoLand.Deno.
- Python: https://www.python.org/ — Python Software Foundation license; installed through winget Python.Python.3.12 if needed.
- Windows Package Manager: https://github.com/microsoft/winget-cli — Microsoft's installed package manager is used when available.

Version identifiers and available formats change over time. Upstream platform support is not a guarantee that every URL works. No third-party affiliation is implied.
