# -*- mode: python ; coding: utf-8 -*-
import importlib.metadata
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_dynamic_libs
from PyInstaller.utils.hooks import copy_metadata

datas = []
binaries = []

try:
    import paddlex
    from paddlex.utils.deps import BASE_DEP_SPECS
    deps_all = list(BASE_DEP_SPECS.keys())
except ImportError:
    raise RuntimeError("paddlex not installed or BASE_DEP_SPECS not found. Please install paddlex first.")

deps_need = deps_all
for dep in deps_need:
    try:
        datas += copy_metadata(dep)
    except Exception as e:
        print(f"Warning: Failed to copy metadata for '{dep}': {e}")

datas += collect_data_files('paddlex')

binaries += collect_dynamic_libs('paddle')

# GPU
try:
    importlib.metadata.version("paddlepaddle-gpu")
    binaries += collect_dynamic_libs('nvidia')
except Exception:
    pass

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
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
    name='OnmyojiDesktopAssistant',
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
    uac_admin=True,
    icon=['src/ui/buzhihuo.jpg'],
    contents_directory='lib',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='output',
)
