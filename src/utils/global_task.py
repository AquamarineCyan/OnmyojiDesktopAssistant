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
                    logger.error(traceback.format_exception(e))
                time.sleep(0.05)
            time.sleep(0.1)

    def stop(self):
        self.running = False
        self.join(1)


global_task = GlobalTask()
