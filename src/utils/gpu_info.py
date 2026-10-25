import asyncio  # noqa: F401  必须在替换 subprocess.Popen 前加载，否则 asyncio.windows_utils 的 Popen 子类化会失败
import os
import shutil
import subprocess

from .log import logger

_CREATE_NO_WINDOW = 0x08000000


def _find_nvidia_smi() -> str | None:
    """定位 nvidia-smi：优先 PATH，其次 System32，返回可执行路径或 None"""
    try:
        exe = shutil.which("nvidia-smi")
        if exe:
            return exe
        sys_path = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32", "nvidia-smi.exe")
        return sys_path if os.path.isfile(sys_path) else None
    except Exception as e:
        logger.warning(f"定位 nvidia-smi 失败: {e}")
        return None


def _query_nvidia_smi(args: list[str]) -> str | None:
    """调用 nvidia-smi 并返回输出文本，任何异常均不外抛"""
    try:
        exe = _find_nvidia_smi()
        if not exe:
            return None
        proc = subprocess.run(
            [exe, *args],
            capture_output=True,
            text=True,
            encoding="gbk",
            errors="ignore",
            timeout=15,
            creationflags=_CREATE_NO_WINDOW,
        )
        if proc.returncode == 0:
            return proc.stdout
        logger.warning(f"nvidia-smi 返回码 {proc.returncode}: {(proc.stderr or '').strip()}")
    except Exception as e:
        logger.warning(f"调用 nvidia-smi 失败: {e}")
    return None


def get_gpu_list() -> list[dict]:
    """返回所有 NVIDIA 显卡信息列表，index 与 PaddleOCR 的 gpu:N 编号对应

    Returns:
        list[dict]: [{"index": 0, "name": "...", "memory_total": 8192, ...}]
    """
    try:
        stdout = _query_nvidia_smi(
            [
                "--query-gpu=index,name,memory.total,memory.used,memory.free,temperature.gpu,driver_version",
                "--format=csv,noheader,nounits",
            ]
        )
        if not stdout:
            return []

        gpus = []
        for line in (s for s in stdout.strip().splitlines() if s):
            fields = [f.strip() for f in line.split(",")]
            if len(fields) < 7:
                continue
            try:
                gpus.append(
                    {
                        "index": int(fields[0]),
                        "name": fields[1],
                        "memory_total": int(fields[2]),
                        "memory_used": int(fields[3]),
                        "memory_free": int(fields[4]),
                        "temperature": int(float(fields[5])),
                        "driver": fields[6],
                    }
                )
            except ValueError:
                continue
        return gpus
    except Exception as e:
        logger.warning(f"解析 nvidia-smi 输出失败: {e}")
        return []


def get_cuda_device_list() -> list[str]:
    """通过 Paddle 查询 CUDA 可见的 NVIDIA 显卡名称列表

    索引与 PaddleOCR 的 device=gpu:N 编号一一对应（仅 NVIDIA 卡参与 CUDA 编号）。

    Returns:
        list[str]: 显卡名称列表，空列表表示当前 Paddle 无 CUDA 设备可用
    """
    try:
        from .ocr_engine.paddleocr import paddle_hide_window_context

        with paddle_hide_window_context():
            import paddle  # noqa: PLC0415

        if not paddle.is_compiled_with_cuda():
            return []
        count = paddle.device.cuda.device_count()
        if count <= 0:
            return []
        return [paddle.device.cuda.get_device_name(i) for i in range(count)]
    except Exception:
        return []


def resolve_device(gpu_id: int | None = None) -> str | None:
    """根据配置的 GPU 编号解析 PaddleOCR 的 device 参数

    Args:
        gpu_id: -1/None 自动（不指定 device，由 Paddle 默认选择）；>=0 手动指定

    Returns:
        device 参数值，如 "gpu:1"；无需指定时返回 None
    """
    if gpu_id is None or gpu_id < 0:
        return None
    return f"gpu:{gpu_id}"


def _log_nvidia_smi(gpus: list[dict]) -> None:
    """输出驱动层面（nvidia-smi）的全部显卡信息"""
    if not gpus:
        logger.ui_error("未找到 nvidia-smi 或未检测到 NVIDIA 显卡，无法获取驱动层面信息，请使用普通版本！")
        return
    for gpu in gpus:
        logger.ui(
            f"GPU[{gpu['index']}] {gpu['name']} | 驱动 {gpu['driver']} | "
            f"显存 {gpu['memory_used'] / 1024:.1f}/{gpu['memory_total'] / 1024:.1f} GB "
            f"(空闲 {gpu['memory_free'] / 1024:.1f} GB) | 温度 {gpu['temperature']}°C"
        )


def _log_paddle_gpu() -> None:
    """输出 Paddle 视角的 GPU 信息并做一次真实运算验证"""
    try:
        from .ocr_engine.paddleocr import paddle_hide_window_context

        with paddle_hide_window_context():
            import paddle  # noqa: PLC0415

        if not paddle.is_compiled_with_cuda():
            logger.ui_warn("当前 Paddle 未编译 CUDA 支持，GPU 加速不可用")
            return
        count = paddle.device.cuda.device_count()
        if count <= 0:
            logger.ui_warn("CUDA 已编译，但未检测到可用 GPU 设备")
            return

        paddle.device.set_device("gpu:0")
        names = ", ".join(paddle.device.cuda.get_device_name(i) for i in range(count))
        logger.ui(f"Paddle 检测到 {count} 块 GPU: {names}")
        logger.ui(f"Paddle 设备: {paddle.device.get_device()} | CUDA 版本: {paddle.version.cuda()}")

        x = paddle.rand([2048, 2048], dtype="float32")
        paddle.matmul(x, x)
        paddle.device.cuda.synchronize()
        logger.ui("GPU 运算验证通过（矩阵乘法已在显卡上完成）")
    except Exception as e:
        logger.ui_warn(f"Paddle GPU 检测失败: {e}")


def log_gpu_info():
    """输出本机显卡信息，供 exe 启动时调用（任何异常均不向上抛出）"""
    try:
        logger.info("start check gpu info")
        gpus = get_gpu_list()
        _log_nvidia_smi(gpus)
        if get_cuda_device_list():
            logger.ui_hint("可在设置中选择用于 OCR 的 GPU 编号（默认 0，与实际使用可用的 N 卡一致）")
        _log_paddle_gpu()
    except Exception as e:
        logger.warning(f"GPU 信息查询失败，已忽略: {e}")
