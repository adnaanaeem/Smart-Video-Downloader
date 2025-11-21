; Inno Setup Script for Smart Video Downloader v2.1.1
; Created by Adnan Naeem

[Setup]
; This unique ID must NOT change between versions.
AppId={{C6A8E3A8-245B-44A7-927A-1A8C8F7E4B3F}}
AppName=Smart Video Downloader
AppVersion=2.1.1
AppPublisher=Adnan Naeem
DefaultDirName={autopf}\Smart Video Downloader
DisableProgramGroupPage=yes
; The folder where the final setup.exe will be saved.
OutputDir=C:\ADNAN\YT-Downloader\Output
OutputBaseFilename=SmartVideoDownloaderSetup-v2.1.1
SetupIconFile=C:\ADNAN\YT-Downloader\icon.ico
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
Source: "C:\ADNAN\YT-Downloader\dist\Smart Video Downloader.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Smart Video Downloader"; Filename: "{app}\Smart Video Downloader.exe"
Name: "{group}\{cm:UninstallProgram,Smart Video Downloader}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Smart Video Downloader"; Filename: "{app}\Smart Video Downloader.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Smart Video Downloader.exe"; Description: "{cm:LaunchProgram,Smart Video Downloader}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

