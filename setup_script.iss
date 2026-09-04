; Inno Setup Script for Smart Video Downloader v2.2.0
; Created by Adnan Naeem
;
; Paths below are relative to this .iss file's own directory (the repo root),
; which Inno Setup resolves automatically - run ISCC.exe from the repo root
; (locally or in CI) after a PyInstaller build has produced dist\.

[Setup]
; This unique ID must NOT change between versions.
AppId={{C6A8E3A8-245B-44A7-927A-1A8C8F7E4B3F}}
AppName=Smart Video Downloader
AppVersion=2.2.0
AppPublisher=Adnan Naeem
DefaultDirName={autopf}\Smart Video Downloader
DisableProgramGroupPage=yes
; The folder where the final setup.exe will be saved.
OutputDir=Output
; Version-agnostic filename so README/CI links to /releases/latest/download/... never go stale.
OutputBaseFilename=SmartVideoDownloaderSetup-Windows
SetupIconFile=icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}";

[Files]
; This bundles the main executable created by PyInstaller.
Source: "dist\Smart Video Downloader.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Smart Video Downloader"; Filename: "{app}\Smart Video Downloader.exe"
Name: "{group}\{cm:UninstallProgram,Smart Video Downloader}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Smart Video Downloader"; Filename: "{app}\Smart Video Downloader.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Smart Video Downloader.exe"; Description: "{cm:LaunchProgram,Smart Video Downloader}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

