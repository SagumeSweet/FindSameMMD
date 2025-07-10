import logging
from logging import Handler
from typing import Optional


class Logger:
    def __init__(self, name: str = "AppLogger", level: int = logging.DEBUG) -> None:
        self._logging = logging.getLogger(name)
        self._logging.setLevel(level)
        self._logging.propagate = False  # 避免重复输出
        self._handler: Optional[Handler] = None

    def set_handler_level(self, level: int) -> None:
        """设置日志处理器的日志级别"""
        if self._handler:
            self._handler.setLevel(level)
        else:
            raise ValueError("Handler is not set. Please set a handler before changing its level.")

    def debug(self, msg, *args, **kwargs):
        self._logging.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._logging.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._logging.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._logging.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self._logging.critical(msg, *args, **kwargs)


class ThreadSafeLogger(Logger):
    def __init__(self, name: str = "AppLogger", level: int = logging.DEBUG) -> None:
        super().__init__(name, level)
        self._formatter = logging.Formatter(
            '[%(asctime)s][%(levelname)s][%(threadName)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler = logging.FileHandler('app.log', mode='w', encoding='utf-8')
        file_handler.setFormatter(self._formatter)
        file_handler.setLevel(level)
        self._logging.addHandler(file_handler)

        self._handler = logging.StreamHandler()
        self._handler.setFormatter(self._formatter)
        self._logging.addHandler(self._handler)
        self.set_handler_level(level)
