#define AppName "Ember Table"
#define AppVersion "0.6.0"
[Setup]
AppId={{E930F682-54A4-4A14-8AA7-4B65FF7AFD17}
AppName={#AppName}
AppVersion={#AppVersion}
DefaultDirName={localappdata}\Programs\EmberTable
DefaultGroupName={#AppName}
PrivilegesRequired=lowest
OutputDir=installer-output
OutputBaseFilename=EmberTable-Setup-0.6.0
Compression=lzma2
SolidCompression=yes
UsePreviousTasks=no
WizardStyle=modern
SetupIconFile=app\ember-table.ico
AppPublisher=Ember Table community project
AppComments=Offline tabletop campaign companion
UninstallDisplayIcon={app}\EmberTable.exe
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"
[Files]
Source: "dist\EmberTable\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\EmberTable.exe"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\EmberTable.exe"; Tasks: desktopicon
[Run]
Filename: "{app}\EmberTable.exe"; Description: "Open Ember Table"; Flags: nowait postinstall skipifsilent
