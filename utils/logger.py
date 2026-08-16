#!/usr/bin/env python
# encoding: utf-8
import logging
import os
import threading
from logging.handlers import RotatingFileHandler


class _LoggerProxy:
    """Proxy that always delegates to the current configured logger.
    This allows reconfiguration at runtime without breaking imports."""

    def __init__(self):
        self._lock = threading.Lock()
        self._logger = self._create_default_logger()

    def _create_default_logger(self):
        _logger = logging.getLogger("app")
        if not _logger.handlers:
            console_handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            _logger.setLevel(logging.INFO)
            _logger.addHandler(console_handler)
        return _logger

    def _reconfigure(self, log_level, log_file_name, log_file_size, log_backup_count):
        """Reconfigure the underlying logger."""
        # Serialize handler swaps so background threads logging concurrently
        # never observe a half-configured logger.
        with self._lock:
            _logger = logging.getLogger("app")

            # Clear existing handlers
            for handler in _logger.handlers[:]:
                _logger.removeHandler(handler)

            log_dir = "logs"
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)

            file_handler = RotatingFileHandler(
                os.path.join(log_dir, log_file_name),
                maxBytes=log_file_size,
                backupCount=log_backup_count
            )
            console_handler = logging.StreamHandler()

            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            _logger.setLevel(log_level)
            file_handler.setLevel(log_level)
            console_handler.setLevel(log_level)

            _logger.addHandler(file_handler)
            _logger.addHandler(console_handler)

            self._logger = _logger

    def __getattr__(self, name):
        return getattr(self._logger, name)


logger = _LoggerProxy()


def init_logger():
    """Reinitialize logger with config parameters from Application."""
    from app import Application

    log_level = logging.INFO
    if Application.setting and Application.setting.LOG_LEVEL:
        log_level = getattr(logging, Application.setting.LOG_LEVEL.upper(), logging.INFO)

    log_file_name = "app.log"
    if Application.setting and Application.setting.LOG_FILE_NAME:
        log_file_name = Application.setting.LOG_FILE_NAME

    log_file_size = 10*1024*1024
    if Application.setting and Application.setting.LOG_FILE_SIZE:
        log_file_size = Application.setting.LOG_FILE_SIZE

    log_backup_count = 5
    if Application.setting and Application.setting.LOG_BACKUP_COUNT:
        log_backup_count = Application.setting.LOG_BACKUP_COUNT

    logger._reconfigure(log_level, log_file_name, log_file_size, log_backup_count)
    return logger
