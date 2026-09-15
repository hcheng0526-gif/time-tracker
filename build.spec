# build.spec
a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[
        "database.db_manager",
        "widgets.timer_widget",
        "widgets.stats_widget",
        "widgets.range_stats_card",
        "widgets.calendar_widget",
        "components.dialogs",
        "components.styles",
        "config",
        "utils"
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['hook-runtime.py'], # 新增这一行！
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True, # 先改成True！调试，看到报错，成功后再改False
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
