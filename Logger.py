import logging

from FileScanner import IScannerLogger


class ThreadSafeLogger(IScannerLogger):
    def __init__(self, name: str = "AppLogger", level: int = logging.INFO) -> None:
        self._logging = logging.getLogger(name)
        self._logging.setLevel(level)
        self._logging.propagate = False  # 避免重复输出
        self._formatter = logging.Formatter(
            '[%(asctime)s][%(levelname)s][%(threadName)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler = logging.FileHandler('app.log', mode='w', encoding='utf-8')
        file_handler.setFormatter(self._formatter)
        file_handler.setLevel(level)
        self._logging.addHandler(file_handler)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(self._formatter)
        stream_handler.setLevel(level)
        self._logging.addHandler(stream_handler)

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
