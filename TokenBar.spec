# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py', 'login_window.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['rumps', 'keyring.backends.macOS', 'webview'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TokenBar',
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
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TokenBar',
)
app = BUNDLE(
    coll,
    name='TokenBar.app',
    icon='TokenBar.icns',
    bundle_identifier='com.user.tokenbar',
    info_plist={
        'LSUIElement': True,
        'NSHighResolutionCapable': True,
        'CFBundleDisplayName': 'TokenBar',
        'CFBundleVersion': '0.1.0',
    },
)
