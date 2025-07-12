import time
from threading import Lock, Thread


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
                task()
                time.sleep(0.05)
            time.sleep(0.1)

    def stop(self):
        self.running = False
        self.join(1)


global_task = GlobalTask()
