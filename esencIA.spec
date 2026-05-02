# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

# Recolectar metadatos y dependencias críticas
datas, binaries, hiddenimports = collect_all('imageio')
datas2, binaries2, hiddenimports2 = collect_all('moviepy')
datas3, binaries3, hiddenimports3 = collect_all('faster_whisper')
datas4, binaries4, hiddenimports4 = collect_all('ctranslate2')

# Combinar todas las recolecciones
datas += datas2 + datas3 + datas4
binaries += binaries2 + binaries3 + binaries4
hiddenimports += hiddenimports2 + hiddenimports3 + hiddenimports4

# Añadir los recursos manuales del proyecto (UI)
datas += [('src/ui', 'src/ui')]

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'PyQt6.QtBluetooth',
        'PyQt6.QtDBus',
        'PyQt6.QtDesigner',
        'PyQt6.QtHelp',
        'PyQt6.QtMultimedia',
        'PyQt6.QtNfc',
        'PyQt6.QtPdf',
        'PyQt6.QtPositioning',
        'PyQt6.QtQml',
        'PyQt6.QtQuick',
        'PyQt6.QtRemoteObjects',
        'PyQt6.QtSensors',
        'PyQt6.QtSerialPort',
        'PyQt6.QtSql',
        'PyQt6.QtTest',
        'PyQt6.QtXml',
        'PyQt6.QtVirtualKeyboard',
        'tkinter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='esencIA',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['src\\ui\\assets\\icon.ico'],
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='esencIA',
)
