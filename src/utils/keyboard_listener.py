import threading
import time

from pynput import keyboard

from .log import logger
from .signals import signal_manager


class KeyListenerThread(threading.Thread):
    """
    键盘监听线程

    - 监听所有功能键(F1-F12)的按下事件
    - 通过回调函数通知按键事件
    """

    DEBOUNCE: float = 0.3
    """同一功能键的最小触发间隔（秒）

    pynput 在按键长按时会持续触发 auto-repeat，不去抖的话长按快捷键
    会让「开始/停止」反复横跳。
    """

    def __init__(self):
        # 必须守护线程：stop() 只 join(timeout=2.0)，若 pynput 内部线程卡住，
        # 非守护线程会阻止解释器退出，程序关不掉
        super().__init__(name="KeyListenerThread", daemon=True)
        self._running = False
        self._listener = None
        self._stop_event = threading.Event()
        self._last_fired: dict[str, float] = {}

        # 功能键列表 (F1-F12)
        self.function_keys = {
            keyboard.Key.f1,
            keyboard.Key.f2,
            keyboard.Key.f3,
            keyboard.Key.f4,
            keyboard.Key.f5,
            keyboard.Key.f6,
            keyboard.Key.f7,
            keyboard.Key.f8,
            keyboard.Key.f9,
            keyboard.Key.f10,
            keyboard.Key.f11,
            keyboard.Key.f12,
        }

    def run(self):
        """线程主循环"""
        self._running = True
        self._stop_event.clear()

        def on_key_press(key):
            try:
                name = key.name
            except AttributeError:
                name = f"Key pressed: {key}"
            if name not in {k.name for k in self.function_keys}:
                return

            now = time.monotonic()
            if now - self._last_fired.get(name, 0.0) < self.DEBOUNCE:
                return
            self._last_fired[name] = now
            signal_manager.main.key_pressed.emit(name)

        self._listener = keyboard.Listener(on_press=on_key_press)
        self._listener.start()

        while self._running:
            if self._stop_event.wait(timeout=0.1):
                break

        if self._listener and self._listener.is_alive():
            self._listener.stop()
        self._listener = None

    def stop(self):
        if not self._running:
            return

        self._running = False
        self._stop_event.set()

        if self.is_alive():
            self.join(timeout=2.0)

        if self.is_alive():
            logger.warning("Key listener thread did not stop gracefully")
