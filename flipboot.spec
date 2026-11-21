# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['flipboot_entry.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['flipboot', 'flipboot.main', 'flipboot.ui', 'flipboot.detector', 'flipboot.security', 'flipboot.tool_checker', 'flipboot.uefi_strategy', 'flipboot.legacy_strategy', 'ctypes', 'subprocess', 'platform', 'hashlib', 'urllib.request'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'pandas', 'scipy', 'PIL', 'PyQt5', 'PyQt6', 'wx', 'test', 'tests'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='FlipBoot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.txt',
)
