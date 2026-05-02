; Script de Inno Setup para esencIA
; ---------------------------------

#define MyAppName "esencIA"
#define MyAppVersion "0.2.0"
#define MyAppPublisher "esencIA Team"
#define MyAppExeName "esencIA.exe"
#define MyIconPath "src\ui\assets\icon.ico"

[Setup]
; AppId único para este proyecto
AppId={{84409748-0A3A-4ABC-AF70-5C26288FB582}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
; Ruta de salida del instalador (Setup.exe)
OutputDir=dist\installer
OutputBaseFilename=esencIA_Setup
SetupIconFile={#MyIconPath}
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Ahora incluimos toda la carpeta generada por PyInstaller
Source: "dist\esencIA\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Opción para ejecutar al finalizar, solicitada por el usuario
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
