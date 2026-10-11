import time
import traceback
from threading import Lock, Thread

from .log import logger


class GlobalTask(Thread):
    """全局任务类，用于管理和执行全局任务"""

    def __init__(self):
        super().__init__(name="GlobalTask", daemon=True)
        self.tasks: list = []  # 存储任务的列表
        self.lock: Lock = Lock()
        self.running: bool = False

    def add(self, func):
        with self.lock:
            self.tasks.append(func)

    def run(self):
        self.running = True
        while self.running:
            with self.lock:
                current_tasks = self.tasks.copy()  # 复制当前任务列表，避免执行时修改
            for task in current_tasks:
                if not self.running:
                    break
                try:
                    task()
                except Exception as e:
                    # 单个任务异常不应导致整个全局任务线程退出
                    logger.error(f"全局任务执行失败: {e}")
                    # format_exception 返回的是 list，直接丢给 logger 会渲染成
                    # Python list repr，必须 join 成真正的堆栈文本
                    logger.error("".join(traceback.format_exception(e)))
                time.sleep(0.05)
            time.sleep(0.1)

    STOP_JOIN_TIMEOUT: float = 5.0
    """停止时等待线程退出的最长时间（秒）

    原来只等 1 秒，但任务里可能正卡在 1 秒的 sleep 或 mumu-cli 的
    10 秒子进程里 —— 等不到就返回，线程随后仍会向已销毁的 Qt 控件发信号。
    """

    def stop(self):
        self.running = False
        if not self.is_alive():
            return
        self.join(self.STOP_JOIN_TIMEOUT)
        if self.is_alive():
            logger.warning("全局任务线程未能在超时内退出，将强制结束")
            # 守护线程本就会被解释器回收；这里只是明确记录一下状态
            logger.debug(f"GlobalTask still alive: is_alive={self.is_alive()}")


global_task = GlobalTask()
