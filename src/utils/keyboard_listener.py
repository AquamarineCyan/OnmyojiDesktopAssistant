import threading

from pynput import keyboard

from .log import logger
from .mysignal import global_ms as ms


class KeyListenerThread(threading.Thread):
    """
    键盘监听线程

    - 监听所有功能键(F1-F12)的按下事件
    - 通过回调函数通知按键事件
    """

    def __init__(self):
        super().__init__(name="KeyListenerThread")
        self._running = False
        self._listener = None
        self._stop_event = threading.Event()

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
                if key in self.function_keys:
                    ms.main.key_pressed.emit(key.name)
            except AttributeError:
                ms.main.key_pressed.emit(f"Key pressed: {key}")

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
