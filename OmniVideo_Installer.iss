; Inno Setup 6 Script — OmniVideo Studio
; Suite Audiovisual Todo-en-Uno (Mejora, Fluidez 60 FPS, Escalado 4K & Modo Cadena)
; Tu Tiendita IA — https://tutiendita-ia.store

#define AppName "OmniVideo Studio"
#define AppVersion "1.0"
#define AppPublisher "Tu Tiendita IA"
#define AppURL "https://tutiendita-ia.store"
#define Raiz ".."

[Setup]
AppId={{C78F591A-8B1E-4E32-9F01-7E1A2C3B4D5E}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion} — Edición Creadores (Tu Tiendita IA)
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
PrivilegesRequired=lowest
DefaultDirName={localappdata}\Programs\Tu Tiendita IA\OmniVideo Studio
DefaultGroupName=Tu Tiendita IA\OmniVideo Studio
DisableProgramGroupPage=no
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
OutputDir={#Raiz}\Instaladores\05 OmniVideo Studio\Instalador
OutputBaseFilename=OmniVideo Studio Instalador 1.0
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
SetupIconFile={#Raiz}\iconos\omnisuite.ico
UninstallDisplayIcon={app}\OmniVideo Studio.exe
UninstallDisplayName={#AppName}

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "{#Raiz}\Instaladores\05 OmniVideo Studio\Portable\OmniVideo Studio Portable\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\OmniVideo Studio.exe"; IconFilename: "{app}\iconos\omnisuite.ico"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\OmniVideo Studio.exe"; IconFilename: "{app}\iconos\omnisuite.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\OmniVideo Studio.exe"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
