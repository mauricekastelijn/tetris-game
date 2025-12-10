# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Tetris Ultimate Edition

This spec file creates a standalone Windows executable that includes all necessary
modules and dependencies. The executable is packaged as a single file with the
console window hidden for a polished user experience.

Build with: pyinstaller tetris.spec
Output: dist/tetris.exe
"""

block_cipher = None

a = Analysis(
    ['src/tetris.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'src',
        'src.config',
        'src.game_states',
        'src.tetromino',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='tetris',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Hide console window for production release
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add path to .ico file if available
)
