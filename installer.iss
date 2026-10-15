#define AppName "RAINY Татагч"
#define AppVersion "2.2.1"
[Setup]
AppId={{BAAAB15C-C0EA-4792-896A-808943FB0519}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=RAINY
DefaultDirName={localappdata}\Programs\RAINY
DefaultGroupName=RAINY Татагч
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=release
OutputBaseFilename=RAINY-Setup
SetupIconFile=extension\icons\rainy.ico
UninstallDisplayIcon={app}\RAINY.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes
RestartApplications=no
[Files]
Source: "dist\RAINY\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Tasks]
Name: "desktopicon"; Description: "Desktop дээр RAINY дүрс үүсгэх"; Flags: checkedonce
Name: "autostart"; Description: "Windows нэвтрэхэд RAINY эхлүүлэх"; Flags: unchecked
[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "RAINYDownloader"; ValueData: """{app}\RAINY.exe"""; Flags: uninsdeletevalue; Tasks: autostart
[Icons]
Name: "{group}\RAINY Татагч"; Filename: "{app}\RAINY.exe"
Name: "{autodesktop}\RAINY Татагч"; Filename: "{app}\RAINY.exe"; Tasks: desktopicon
[Run]
Filename: "{app}\RAINY.exe"; Parameters: "--register"; Flags: runhidden waituntilterminated
Filename: "{app}\RAINY.exe"; Description: "RAINY Татагч нээх"; Flags: nowait postinstall skipifsilent
[UninstallRun]
Filename: "{app}\RAINY.exe"; Parameters: "--unregister"; Flags: runhidden waituntilterminated
