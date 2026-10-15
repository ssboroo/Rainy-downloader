param([ValidatePattern('^[a-p]{32}$')][string]$ExtensionId = 'fpkmjpbhnffggibaenfhnacakkcpfbmc')
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$sourceRoot = Split-Path $PSScriptRoot -Parent
$installRoot = Join-Path $env:LOCALAPPDATA 'RAINYDownloader'
function Refresh-UserPath {
    $env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [Environment]::GetEnvironmentVariable('Path','User')
}
function Install-PackageIfNeeded([string]$CommandName,[string]$PackageId) {
    if (Get-Command $CommandName -ErrorAction SilentlyContinue) { return }
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) { throw 'winget олдсонгүй. Microsoft App Installer-ийг суулгаад дахин ажиллуулна уу.' }
    Write-Host "Хэрэгсэл суулгаж байна: $PackageId"
    & winget install --exact --id $PackageId --scope user --accept-source-agreements --accept-package-agreements --disable-interactivity
    Refresh-UserPath
    if (-not (Get-Command $CommandName -ErrorAction SilentlyContinue)) { throw "$CommandName суусангүй. README-MN.md зааврын дагуу суулгаад дахин ажиллуулна уу." }
}
try {
    Write-Host ''
    Write-Host 'RAINY Татагч · Windows суулгац' -ForegroundColor Cyan
    Write-Host 'Хамаарлуудыг албан ёсны багцын сангаас суулгана. Интернэт шаардлагатай.'
    Refresh-UserPath
    $pythonCommand = Get-Command py -ErrorAction SilentlyContinue
    if ($pythonCommand) {
        $pythonExe = & py -3 -c "import sys; print(sys.executable)" 2>$null
    } else { $pythonExe = $null }
    if (-not $pythonExe -and (Get-Command python -ErrorAction SilentlyContinue)) {
        $pythonExe = & python -c "import sys; print(sys.executable)" 2>$null
    }
    if (-not $pythonExe) {
        Install-PackageIfNeeded 'py' 'Python.Python.3.12'
        $pythonExe = & py -3 -c "import sys; print(sys.executable)"
    }
    if (-not $pythonExe -or -not (Test-Path $pythonExe)) { throw 'Python олдсонгүй. Python 3.11+ суулгаад дахин ажиллуулна уу.' }
    & $pythonExe -c "import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)"
    if ($LASTEXITCODE -ne 0) { throw 'Python 3.11 эсвэл түүнээс шинэ хувилбар шаардлагатай.' }
    Install-PackageIfNeeded 'ffmpeg' 'Gyan.FFmpeg'
    Install-PackageIfNeeded 'deno' 'DenoLand.Deno'
    if (-not (Get-Command ffprobe -ErrorAction SilentlyContinue)) { throw 'ffprobe дутуу байна. FFmpeg багцыг бүрэн суулгана уу.' }
    New-Item -ItemType Directory -Force -Path $installRoot | Out-Null
    # Reinstallation is blocked while the worker owns its lock.
    $lockPath = Join-Path $installRoot 'data\worker.lock'
    if (Test-Path $lockPath) {
        try { $lock = [IO.File]::Open($lockPath,'Open','ReadWrite','None'); $lock.Dispose() }
        catch { throw 'Татагч ажиллаж байна. Таталтуудаа дуусгаад эсвэл цуцлаад, Chrome-оо хааж 2 минутын дараа дахин суулгана уу.' }
    }
    foreach ($folder in @('host','extension')) {
        $dest = Join-Path $installRoot $folder
        if (Test-Path $dest) { Remove-Item -LiteralPath $dest -Recurse -Force }
        Copy-Item -LiteralPath (Join-Path $sourceRoot $folder) -Destination $installRoot -Recurse
    }
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'start-host.cmd') -Destination $installRoot -Force
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'uninstall.ps1') -Destination $installRoot -Force
    & $pythonExe -m venv (Join-Path $installRoot '.venv')
    if ($LASTEXITCODE -ne 0) { throw 'Python орчин үүсгэж чадсангүй.' }
    $venvPython = Join-Path $installRoot '.venv\Scripts\python.exe'
    & $venvPython -m pip install --upgrade 'yt-dlp[default]'
    if ($LASTEXITCODE -ne 0) { throw 'yt-dlp суулгах үед алдаа гарлаа. Интернэтээ шалгана уу.' }
    $ffmpegFolder = Split-Path (Get-Command ffmpeg).Source -Parent
    $ffprobeFolder = Split-Path (Get-Command ffprobe).Source -Parent
    $denoFolder = Split-Path (Get-Command deno).Source -Parent
    Push-Location $installRoot
    try {
        & $venvPython -m host.install_config $installRoot $ExtensionId $ffmpegFolder $ffprobeFolder $denoFolder
        if ($LASTEXITCODE -ne 0) { throw 'Холболтын файл үүссэнгүй.' }
        & $venvPython -c "from host.runtime import health; import json,sys; h=health(); print(json.dumps(h,ensure_ascii=False)); sys.exit(0 if h['ready'] else 1)"
        if ($LASTEXITCODE -ne 0) { throw 'Хамаарлын шалгалт амжилтгүй.' }
        & $venvPython -m pip freeze | Set-Content -Encoding UTF8 (Join-Path $installRoot 'installed-versions.txt')
    } finally { Pop-Location }
    $registryKey = 'HKCU:\Software\Google\Chrome\NativeMessagingHosts\mn.rainy.downloader'
    New-Item -Path $registryKey -Force | Out-Null
    Set-Item -Path $registryKey -Value (Join-Path $installRoot 'mn.rainy.downloader.json')
    Write-Host ''
    Write-Host 'Туслах програм амжилттай суулгагдлаа.' -ForegroundColor Green
    Write-Host 'Одоо chrome://extensions нээгээд Developer mode → Load unpacked сонгоно.'
    Write-Host "Сонгох хавтас: $installRoot\extension"
    Write-Host "Хүлээгдэж буй ID: $ExtensionId"
    Write-Host 'Өргөтгөлийг ачаалаад баруун дээд талд бэхэлнэ. Chrome-оо бүрэн хааж дахин нээгээрэй.'
    Start-Process explorer.exe -ArgumentList ('"' + (Join-Path $installRoot 'extension') + '"')
} catch {
    Write-Host ''
    Write-Host ('Суулгац дууссангүй: ' + $_.Exception.Message) -ForegroundColor Red
    exit 1
}
