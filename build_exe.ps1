# Script para generar el ejecutable de esencIA
# Asegúrate de tener instalado PyInstaller en tu entorno virtual:
# pip install pyinstaller

Write-Host "Iniciando proceso de construcción de esencIA.exe..." -ForegroundColor Cyan

# Directorio de salida
$DistDir = "dist"
if (Test-Path $DistDir) {
    Remove-Item -Recurse -Force $DistDir
}

# Comando de PyInstaller
# --noconsole: No abre una ventana de terminal
# --onefile: Empaqueta todo en un solo archivo .exe
# --add-data: Incluye archivos de recursos (HTML, iconos, etc.)
# --icon: Icono del archivo ejecutable
# --name: Nombre del ejecutable final

.\venv\Scripts\pyinstaller esencIA.spec

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n¡Éxito! El ejecutable se encuentra en la carpeta '$DistDir'." -ForegroundColor Green
    Write-Host "Recuerda que el usuario final debe tener Ollama instalado para el procesamiento de IA." -ForegroundColor Yellow
} else {
    Write-Host "`nOcurrió un error durante la construcción." -ForegroundColor Red
}
