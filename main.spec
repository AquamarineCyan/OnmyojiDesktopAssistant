# -*- mode: python ; coding: utf-8 -*-
import importlib.metadata
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_dynamic_libs
from PyInstaller.utils.hooks import copy_metadata

datas = []
binaries = []

# RapidOCR 资源：模型清单、默认配置、字典等
# 排除随包分发的默认模型（PP-OCRv6 small，约 31MB）：运行时统一使用 models 目录下的
# 模型文件，由 Global.model_root_dir 指定，不会读取包内 models
datas += [
    entry
    for entry in collect_data_files('rapidocr')
    if not entry[0].lower().endswith('.onnx')
]

# 推理引擎原生库：GPU 版用 PaddlePaddle，CPU 版用 ONNX Runtime
# 两者只会有一个存在（见 requirements-gpu.txt），故按存在性收集
is_gpu = False
try:
    importlib.metadata.version("paddlepaddle-gpu")
    is_gpu = True
    binaries += collect_dynamic_libs('paddle')
    datas += collect_data_files('paddle', include_py_files=True)
    binaries += collect_dynamic_libs('nvidia')
    # 一并带上发行包元数据：GPU 判据以 lib/nvidia 目录为主，
    # 若该目录缺失还能回退查包名，而查包名依赖 dist-info 被一起打包
    try:
        datas += copy_metadata('paddlepaddle-gpu')
    except Exception as e:
        print(f"Warning: Failed to copy metadata for 'paddlepaddle-gpu': {e}")
except Exception:
    pass

if not is_gpu:
    try:
        binaries += collect_dynamic_libs('onnxruntime')
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
