import logging
from logging.handlers import RotatingFileHandler
import os
from typing import Optional
from flask import Flask

class LogConfig:
    """Logging configuration loaded from environment variables"""
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
    LOG_FORMAT = os.getenv('LOG_FORMAT', 
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', 10240000))  # 10MB default
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))
    
    # New configuration options for logging destination
    LOG_TO_CONSOLE = os.getenv('LOG_TO_CONSOLE', 'True').lower() == 'true'
    LOG_TO_FILE = os.getenv('LOG_TO_FILE', 'True').lower() == 'true'
    
    @classmethod
    def get_log_level(cls) -> int:
        """Convert string log level to logging constant"""
        return getattr(logging, cls.LOG_LEVEL.upper())

def create_handlers() -> list:
    """Create and return a list of configured handlers based on environment settings"""
    handlers = []
    formatter = logging.Formatter(LogConfig.LOG_FORMAT)

    # Console handler
    if LogConfig.LOG_TO_CONSOLE:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(LogConfig.get_log_level())
        handlers.append(console_handler)

    # File handler
    if LogConfig.LOG_TO_FILE:
        # Ensure logs directory exists
        log_dir = os.path.dirname(LogConfig.LOG_FILE)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        file_handler = RotatingFileHandler(
            LogConfig.LOG_FILE,
            maxBytes=LogConfig.LOG_MAX_BYTES,
            backupCount=LogConfig.LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(LogConfig.get_log_level())
        handlers.append(file_handler)

    return handlers

def setup_logger(app: Flask) -> None:
    """Configure application logging based on environment settings"""
    handlers = create_handlers()
    
    if not handlers:
        raise ValueError("No logging handlers configured. Set either LOG_TO_CONSOLE=True or LOG_TO_FILE=True")

    # Configure Werkzeug logger (for request/response details)
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(LogConfig.get_log_level())
    for handler in handlers:
        werkzeug_logger.addHandler(handler)

    # Configure MongoDB logger
    mongo_logger = logging.getLogger('mongodb')
    mongo_logger.setLevel(LogConfig.get_log_level())
    for handler in handlers:
        mongo_logger.addHandler(handler)

    # Configure application logger
    app.logger.setLevel(LogConfig.get_log_level())
    for handler in handlers:
        app.logger.addHandler(handler)

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a configured logger instance for a specific module"""
    logger = logging.getLogger(name or __name__)
    
    if not logger.handlers:  # Only add handler if logger doesn't have one
        handlers = create_handlers()
        for handler in handlers:
            logger.addHandler(handler)
        logger.setLevel(LogConfig.get_log_level())
    
    return logger 