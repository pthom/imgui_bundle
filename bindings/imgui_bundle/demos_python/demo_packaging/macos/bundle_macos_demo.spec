# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['bundle_macos_demo.py'],
    pathex=[],
    binaries=[],
    datas=[("assets", "assets")],
    hiddenimports=[],
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
    name='bundle_macos_demo',
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
    name='bundle_macos_demo',
)
app = BUNDLE(
    coll,
    name='bundle_macos_demo.app',
    # icon="logo_imgui_bundle.icns", # provide your own, or copy from imgui_bundle/logo/macOS/logo_imgui_bundle.icns
    bundle_identifier="bundle_macos_demo",
)
