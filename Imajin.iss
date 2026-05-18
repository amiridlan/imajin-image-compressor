; Imajin — Inno Setup installer script
; Download Inno Setup: https://jrsoftware.org/isinfo.php
; Build: Open this file in Inno Setup Compiler and click Build > Compile
; Output: installer\ImajinSetup.exe

#define AppName      "Imajin"
#define AppVersion   "2.0.0"
#define AppPublisher "Amir Idlan"
#define AppExeName   "Imajin.exe"
#define AppURL       "https://github.com/amiridlan/imajin-image-compressor"

[Setup]
; ── Identity ──────────────────────────────────────────────────────────
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}/releases

; ── Install location ──────────────────────────────────────────────────
; PrivilegesRequired=lowest → installs to %LOCALAPPDATA%, no UAC prompt.
; This allows silent auto-update without admin rights.
; Change to "admin" if you prefer a Program Files install (requires UAC).
PrivilegesRequired=lowest
DefaultDirName={localappdata}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes

; ── Output ────────────────────────────────────────────────────────────
OutputDir=installer
OutputBaseFilename=ImajinSetup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern

; ── Allows /SILENT and /VERYSILENT flags (used by auto-updater) ───────
; These flags are built into Inno Setup — no extra configuration needed.

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; \
    GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Main executable produced by PyInstaller
Source: "dist\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\{#AppName}";  Filename: "{app}\{#AppExeName}"; \
    Tasks: desktopicon

[Run]
; Launch app after install (skipped during silent auto-update)
Filename: "{app}\{#AppExeName}"; \
    Description: "{cm:LaunchProgram,{#StringChange(AppName,'&','&&')}}"; \
    Flags: nowait postinstall skipifsilent
