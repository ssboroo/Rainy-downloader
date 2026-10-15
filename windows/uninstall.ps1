$ErrorActionPreference = 'Stop'
$installRoot = Join-Path $env:LOCALAPPDATA 'RAINYDownloader'
$registryKey = 'HKCU:\Software\Google\Chrome\NativeMessagingHosts\mn.rainy.downloader'
try {
    $lockPath = Join-Path $installRoot 'data\worker.lock'
    if (Test-Path $lockPath) {
        try { $lock = [IO.File]::Open($lockPath,'Open','ReadWrite','None'); $lock.Dispose() }
        catch { throw 'Татагч ажиллаж байна. Таталтаа цуцлаад Chrome-оо хааж 2 минутын дараа дахин оролдоно уу.' }
    }
    if (Test-Path $registryKey) {
        $registered = (Get-Item $registryKey).GetValue('')
        if ($registered -eq (Join-Path $installRoot 'mn.rainy.downloader.json')) { Remove-Item $registryKey -Force }
    }
    # Keep history, user settings, downloaded media and shared dependencies.
    foreach ($name in @('host','extension','.venv','start-host.cmd','native-config.json','mn.rainy.downloader.json','installed-versions.txt','uninstall.ps1')) {
        $target = Join-Path $installRoot $name
        if (Test-Path $target) { Remove-Item -LiteralPath $target -Force -Recurse }
    }
    Write-Host 'RAINY туслах програм устгагдлаа. Татсан файлууд болон түүх хадгалагдсан.'
    Write-Host 'Chrome-ийн chrome://extensions хэсгээс өргөтгөлөө Remove дарж устгана уу.'
} catch { Write-Host $_.Exception.Message -ForegroundColor Red; exit 1 }
