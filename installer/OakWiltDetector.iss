; Inno Setup script: wraps the PyInstaller output (dist\OakWiltDetector) into a Setup.exe.
; Build from the repo root after PyInstaller:  iscc /DMyAppVersion=1.0.0 installer\OakWiltDetector.iss

#ifndef MyAppVersion
  #define MyAppVersion "0.0.0"
#endif

#define MyAppName "Oak Wilt Detector"
#define MyAppExe "OakWiltDetector.exe"

[Setup]
; Keep this AppId the same forever so new versions upgrade in place.
AppId={{10E05AC5-EF81-4C1D-B87F-FA7F5C81D697}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=Grand Haven Parks
DefaultDirName={autopf}\OakWiltDetector
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\{#MyAppExe}
; Installs for the current user without admin rights; users with admin can choose all users.
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
SourceDir=..
OutputDir=dist
OutputBaseFilename=OakWiltDetector-Setup-{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "dist\OakWiltDetector\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExe}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent
