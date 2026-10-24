# -*- mode: python ; coding: utf-8 -*-
# Build macOS : pyinstaller --clean --noconfirm RepartitionServices.spec
#
# Application en mode « dossier » (onedir) : le mode « fichier unique » dans un
# .app est déconseillé par PyInstaller sur macOS (le programme tourne dans un
# second processus, ce qui perturbe les fenêtres et les clics).

import os
import re

# Version unique : version.py (VERSION = "x.y")
with open(os.path.join(SPECPATH, "version.py"), encoding="utf-8") as f:
    VERSION = re.search(r'VERSION = "([^"]+)"', f.read()).group(1)

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('preferences_defaut.json', '.')],
    hiddenimports=[
        'interface.fenetre_contraintes',
        'interface.fenetre_resultats',
        'export.export',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='RepartitionServices',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets/icon.icns'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name='RepartitionServices',
)
app = BUNDLE(
    coll,
    name='RepartitionServices.app',
    icon='assets/icon.icns',
    bundle_identifier='io.github.johnburnout.repartitionservices',
    info_plist={
        'CFBundleName': 'RepartitionServices',
        'CFBundleShortVersionString': VERSION,
        'CFBundleVersion': VERSION,
        'NSHighResolutionCapable': True,
    },
)
