$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
if ($env:OS -ne 'Windows_NT') { throw 'Энэ build Windows дээр ажиллана.' }
$root = Split-Path $PSScriptRoot -Parent
Push-Location $root
function Check-Native([string]$Step) { if ($LASTEXITCODE -ne 0) { throw "$Step failed: $LASTEXITCODE" } }
try {
    if (-not (Test-Path '.build-venv\Scripts\python.exe')) {
        if (Get-Command py -ErrorAction SilentlyContinue) { & py -3.12 -m venv .build-venv }
        else { & python -m venv .build-venv }
        Check-Native 'Python venv'
    }
    $python = Join-Path $root '.build-venv\Scripts\python.exe'
    & $python -c "import sys; sys.exit(0 if sys.version_info[:2] == (3,12) else 1)"
    if ($LASTEXITCODE -ne 0) { throw 'Build Python 3.12 шаардлагатай. Python 3.12 суулгаад шинэ хавтсанд задалсан багцаас дахин ажиллуулна уу.' }
    & $python -m pip install -r requirements-desktop.txt 'pyinstaller==6.16.0'
    Check-Native 'Build dependencies'
    & $python -m unittest discover -s tests -v
    Check-Native 'Python tests'
    & node --test tests/extension.test.mjs
    Check-Native 'JavaScript tests'
    & $python -m PyInstaller --noconfirm --clean --onedir --windowed --name RAINY --paths $root --collect-all customtkinter --collect-submodules pywinauto --collect-submodules comtypes --icon extension/icons/rainy.ico desktop/entry.py
    Check-Native 'Desktop EXE'
    & $python -m PyInstaller --noconfirm --clean --onedir --console --name RAINY.Native --paths $root --distpath native-dist --workpath native-build host/native_entry.py
    Check-Native 'Native EXE'
    Copy-Item native-dist/RAINY.Native/RAINY.Native.exe dist/RAINY/ -Force
    Copy-Item native-dist/RAINY.Native/_internal/* dist/RAINY/_internal/ -Recurse -Force
    & $python build-tools/download_tools.py dist/RAINY/tools
    Check-Native 'Verified tool downloads'
    & $python build-tools/browser_extensions.py dist/RAINY/browser-extensions
    Check-Native 'Browser helpers'
    Copy-Item README-DESKTOP-MN.md,THIRD-PARTY-NOTICES.md,VALIDATION-DESKTOP.md dist/RAINY/ -Force
    # Exercise the packaged GUI executable without opening its window.
    $healthPath = Join-Path $root 'dist\health-report.json'
    $process = Start-Process -FilePath (Join-Path $root 'dist\RAINY\RAINY.exe') -ArgumentList @('--health-report',('"' + $healthPath + '"')) -Wait -PassThru
    if ($process.ExitCode -ne 0) { throw 'Packaged tools did not pass health check.' }
    $report = Get-Content -Raw $healthPath | ConvertFrom-Json
    if (-not $report.ready) { throw 'Packaged health report not ready.' }
    $tool = Join-Path $root 'dist\RAINY\tools\yt-dlp.exe'
    Move-Item $tool ($tool + '.test-missing')
    try {
        $missingReport = Join-Path $root 'dist\missing-tool-report.json'
        $missing = Start-Process -FilePath (Join-Path $root 'dist\RAINY\RAINY.exe') -ArgumentList @('--health-report',('"' + $missingReport + '"')) -Wait -PassThru
        if ($missing.ExitCode -eq 0) { throw 'Missing tool unexpectedly passed health.' }
        $missingData = Get-Content -Raw $missingReport | ConvertFrom-Json
        if ($missingData.ready) { throw 'Missing tool report unexpectedly ready.' }
        if (Get-Process -Name RAINY -ErrorAction SilentlyContinue) { throw 'Health test left a GUI/worker process running.' }
    } finally { Move-Item ($tool + '.test-missing') $tool }
    & $python build-tools/smoke_native.py dist/RAINY
    Check-Native 'Packaged Native Messaging'
    $iscc = Join-Path ${env:ProgramFiles(x86)} 'Inno Setup 6\ISCC.exe'
    if (-not (Test-Path $iscc)) { throw 'Inno Setup 6 суулгана уу. winget install JRSoftware.InnoSetup' }
    & $iscc installer.iss
    Check-Native 'Installer'
    Write-Host 'Бэлэн: release\RAINY-Setup.exe' -ForegroundColor Green
} finally { Pop-Location }
