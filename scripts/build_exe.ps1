# Script de automatización de compilación para esencIA
# Genera los binarios con PyInstaller y compila el instalador con Inno Setup (si está instalado).

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
$AppVersion = "0.3.0"
if (Test-Path $VersionFile) {
    $VersionLine = Select-String -Path $VersionFile -Pattern '__version__\s*=\s*"(.*?)"'
    if ($VersionLine -and $VersionLine.Matches.Groups[1].Value) {
        $AppVersion = $VersionLine.Matches.Groups[1].Value
    }
}
Write-Host "Versión detectada: v$AppVersion" -ForegroundColor Green

# Sincronizar automáticamente la versión en scripts/esencia_installer.iss
$IssFile = "$RootDir\scripts\esencia_installer.iss"
if (Test-Path $IssFile) {
    (Get-Content $IssFile) -replace '#define MyAppVersion ".*?"', "#define MyAppVersion ""$AppVersion""" | Set-Content $IssFile
    Write-Host "Sincronizada versión v$AppVersion en scripts/esencia_installer.iss" -ForegroundColor Gray
}

# Directorio de salida
$DistDir = "$RootDir\dist"
$BuildDir = "$RootDir\build"

if (Test-Path $DistDir) {
    Remove-Item -Recurse -Force $DistDir
}
if (Test-Path $BuildDir) {
    Remove-Item -Recurse -Force $BuildDir
}

# 1. Ejecutar PyInstaller usando el spec localizado en scripts
Set-Location $RootDir

$PyInstallerCmd = "pyinstaller"
if (Test-Path "$RootDir\venv\Scripts\pyinstaller.exe") {
    $PyInstallerCmd = "$RootDir\venv\Scripts\pyinstaller.exe"
}

Write-Host "`n[Paso 1/2] Compilando aplicación con PyInstaller..." -ForegroundColor Cyan
& $PyInstallerCmd --noconfirm "$RootDir\scripts\esencIA.spec"

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nOcurrió un error durante la construcción con PyInstaller." -ForegroundColor Red
    exit 1
}

Write-Host "¡Éxito! Binarios generados en '$DistDir\esencIA'." -ForegroundColor Green

# 2. Compilar el Instalador de Windows con Inno Setup (ISCC.exe) si está disponible
Write-Host "`n[Paso 2/2] Buscando compilador de Inno Setup (ISCC.exe)..." -ForegroundColor Cyan

$IsccPaths = @(
    "ISCC.exe",
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles}\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles(x86)}\Inno Setup 5\ISCC.exe",
    "${env:ProgramFiles}\Inno Setup 5\ISCC.exe"
)

$IsccCmd = $null
foreach ($path in $IsccPaths) {
    if (Get-Command $path -ErrorAction SilentlyContinue) {
        $IsccCmd = $path
        break
    } elseif (Test-Path $path) {
        $IsccCmd = $path
        break
    }
}

if ($IsccCmd) {
    Write-Host "Compilando instalador con Inno Setup ($IsccCmd)..." -ForegroundColor Cyan
    & $IsccCmd "$RootDir\scripts\esencia_installer.iss"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n🎉 ¡Proceso Completo! Instalador generado en: '$DistDir\installer\esencIA_Setup.exe'." -ForegroundColor Green
    } else {
        Write-Host "No se pudo generar el instalador con Inno Setup." -ForegroundColor Yellow
    }
} else {
    Write-Host "Nota: Inno Setup (ISCC.exe) no fue localizado automáticamente en las rutas por defecto." -ForegroundColor Yellow
    Write-Host "Puedes compilar el instalador abriendo 'Inno Setup Compiler' y cargando el archivo:" -ForegroundColor Yellow
    Write-Host "   '$RootDir\scripts\esencia_installer.iss'" -ForegroundColor Yellow
}
