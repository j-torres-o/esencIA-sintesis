# Script de automatización de compilación para esencIA
# Asegúrate de ejecutar este script desde la raíz del proyecto o mediante .\scripts\build_exe.ps1

$ErrorActionPreference = "Stop"

# Obtener directorio raíz del proyecto
$RootDir = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path "$RootDir\src\main.py")) {
    $RootDir = Get-Location
}

Write-Host "Iniciando proceso de construcción para esencIA..." -ForegroundColor Cyan
Write-Host "Directorio raíz: $RootDir" -ForegroundColor Gray

# Extraer versión dinámicamente desde src/version.py
$VersionFile = "$RootDir\src\version.py"
$AppVersion = "0.2.0"
if (Test-Path $VersionFile) {
    $VersionLine = Select-String -Path $VersionFile -Pattern '__version__\s*=\s*"(.*?)"'
    if ($VersionLine -and $VersionLine.Matches.Groups[1].Value) {
        $AppVersion = $VersionLine.Matches.Groups[1].Value
    }
}
Write-Host "Versión detectada: v$AppVersion" -ForegroundColor Green

# Directorio de salida
$DistDir = "$RootDir\dist"
$BuildDir = "$RootDir\build"

if (Test-Path $DistDir) {
    Remove-Item -Recurse -Force $DistDir
}
if (Test-Path $BuildDir) {
    Remove-Item -Recurse -Force $BuildDir
}

# Ejecutar PyInstaller usando el spec localizado en scripts
Set-Location $RootDir

$PyInstallerCmd = "pyinstaller"
if (Test-Path "$RootDir\venv\Scripts\pyinstaller.exe") {
    $PyInstallerCmd = "$RootDir\venv\Scripts\pyinstaller.exe"
}

Write-Host "Ejecutando PyInstaller..." -ForegroundColor Cyan
& $PyInstallerCmd --noconfirm "$RootDir\scripts\esencIA.spec"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n¡Éxito en compilación! Ejecutable generado en: '$DistDir\esencIA'." -ForegroundColor Green
    Write-Host "Nota: El usuario final debe tener Ollama configurado localmente para las funciones de IA." -ForegroundColor Yellow
} else {
    Write-Host "`nOcurrió un error durante la construcción con PyInstaller." -ForegroundColor Red
    exit 1
}
