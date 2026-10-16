# -*- mode: python ; coding: utf-8 -*-
import importlib.metadata
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_dynamic_libs
from PyInstaller.utils.hooks import copy_metadata

datas = []
binaries = []

# GPU use PaddleOCR(paddlex + nvidia)
# CPU use RapidOCR + ONNX Runtime
is_gpu = False
try:
    importlib.metadata.version("paddlepaddle-gpu")
    is_gpu = True
except Exception:
    pass

if is_gpu:
    try:
        import paddlex
        from paddlex.utils.deps import BASE_DEP_SPECS
        deps_all = list(BASE_DEP_SPECS.keys())
    except ImportError:
        raise RuntimeError("paddlex not installed or BASE_DEP_SPECS not found. Please install paddlex first.")

    installed_deps = {dist.metadata["Name"] for dist in importlib.metadata.distributions()}
    deps_need = [dep for dep in deps_all if dep in installed_deps]
    
    for dep in deps_need:
        try:
            datas += copy_metadata(dep)
        except Exception as e:
            print(f"Warning: Failed to copy metadata for '{dep}': {e}")

    datas += collect_data_files('paddlex')

    binaries += collect_dynamic_libs('paddle')
    # remove unuse lib files
    nvidia_skip_dirs = (
        'nvidia/cufft',
        'nvidia/curand',
        'nvidia/cusolver',
        'nvidia/cusparse',
        'nvidia/nvjitlink',
    )
    nvidia_skip_files = ('nvidia/cudnn/bin/cudnn_adv64_9.dll',)
    binaries += [
        entry
        for entry in collect_dynamic_libs('nvidia')
        if not entry[1].replace('\\', '/').startswith(nvidia_skip_dirs)
        and entry[1].replace('\\', '/') not in nvidia_skip_files
    ]

    try:
        datas += copy_metadata('paddlepaddle-gpu')
    except Exception as e:
        print(f"Warning: Failed to copy metadata for 'paddlepaddle-gpu': {e}")
else:
    # without model files
    datas += [
        entry
        for entry in collect_data_files('rapidocr')
        if not entry[0].lower().endswith('.onnx')
    ]

    binaries += collect_dynamic_libs('onnxruntime')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter'],
    noarchive=False,
)

skip_binaries = {
    'nvidia/cudnn/bin/cudnn_adv64_9.dll',  # cudnn 注意力子库，OCR 推理未用
    'paddle/libs/warpctc.dll',  # CTC 损失，仅训练用
    'paddle/libs/warprnnt.dll',  # RNN 的 cuDNN 封装，仅训练用
    'paddle/libs/liblapack.dll',  # mingw 版 BLAS 组，OCR 推理未用
    'paddle/libs/libblas.dll',
    'paddle/libs/libgfortran-3.dll',
    'paddle/libs/libquadmath-0.dll',
    'paddle/libs/libgcc_s_seh-1.dll',
}


def _norm_path(name):
    return name.replace('\\', '/')


a.binaries = [
    item
    for item in a.binaries
    if _norm_path(item[0]) not in skip_binaries
]

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
    upx=False,
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
    upx=False,
    name='output',
)
