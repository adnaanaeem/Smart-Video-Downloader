; Inno Setup Script for Smart Video Downloader
; Created by Adnan Naeem

[Setup]
; NOTE: The AppId is a unique identifier for your application.
; It's generated once and should not change between versions.
AppId={{C6A8E3A8-245B-44A7-927A-1A8C8F7E4B3F}}
AppName=Smart Video Downloader
AppVersion=1.0
AppPublisher=Adnan Naeem
DefaultDirName={autopf}\Smart Video Downloader
DisableProgramGroupPage=yes
; The folder where the final setup.exe will be saved.
OutputDir=C:\YT-Downloader\Output
OutputBaseFilename=SmartVideoDownloaderSetup
SetupIconFile=C:\YT-Downloader\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}";

[Files]
; This is the main executable created by PyInstaller.
Source: "C:\YT-Downloader\dist\Smart Video Downloader.exe"; DestDir: "{app}"; Flags: ignoreversion

; NOTE: If you add more files (like a readme.txt), add them here.
; For example: Source: "C:\YT-Downloader\readme.txt"; DestDir: "{app}";

[Icons]
Name: "{group}\Smart Video Downloader"; Filename: "{app}\Smart Video Downloader.exe"
Name: "{group}\{cm:UninstallProgram,Smart Video Downloader}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Smart Video Downloader"; Filename: "{app}\Smart Video Downloader.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Smart Video Downloader.exe"; Description: "{cm:LaunchProgram,Smart Video Downloader}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"