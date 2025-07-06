import logging

class ThreadSafeLogger:
    def __init__(self, name: str = "AppLogger", level: int = logging.DEBUG) -> None:
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False  # 避免重复输出

        formatter = logging.Formatter(
            '[%(asctime)s][%(levelname)s][%(threadName)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)

