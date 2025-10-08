import logging
from logging.handlers import RotatingFileHandler
import os
from typing import Optional
from flask import Flask


class LogConfig:
    """Logging configuration"""
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
    LOG_FORMAT = os.getenv('LOG_FORMAT',
                           '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
                           )

    @classmethod
    def get_log_level(cls) -> int:
        """Convert string log level to logging constant"""
        return getattr(logging, cls.LOG_LEVEL.upper())


def create_handlers() -> list:
    """Create and return console handler for logging"""
    formatter = logging.Formatter(LogConfig.LOG_FORMAT)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(LogConfig.get_log_level())
    return [console_handler]


def setup_logger(app: Flask) -> None:
    """Configure application logging"""
    handlers = create_handlers()

    # Configure Werkzeug logger (for request/response details)
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(LogConfig.get_log_level())
    werkzeug_logger.addHandler(handlers[0])

    # Configure MongoDB logger
    mongo_logger = logging.getLogger('mongodb')
    mongo_logger.setLevel(LogConfig.get_log_level())
    mongo_logger.addHandler(handlers[0])

    # Configure application logger
    app.logger.setLevel(LogConfig.get_log_level())
    app.logger.addHandler(handlers[0])


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a configured logger instance for a specific module"""
    logger = logging.getLogger(name or __name__)

    if not logger.handlers:  # Only add handler if logger doesn't have one
        logger.addHandler(create_handlers()[0])
        logger.setLevel(LogConfig.get_log_level())

    return logger
