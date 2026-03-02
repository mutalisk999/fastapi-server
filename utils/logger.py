import logging
import os
from logging.handlers import RotatingFileHandler

from app import Application

logger = None

def setup_logger(log_level, log_file_name, log_file_size, log_backup_count):
    logger = logging.getLogger()
    
    # Clear existing handlers to avoid duplication
    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)

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
    
    logger.setLevel(log_level)
    file_handler.setLevel(log_level)
    console_handler.setLevel(log_level)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def init_logger():
    global logger

    # Get log level
    log_level = logging.INFO
    if Application.setting and Application.setting.LOG_LEVEL:
        log_level = getattr(logging, Application.setting.LOG_LEVEL.upper(), logging.INFO)
    
    # Get log file name
    log_file_name = "app.log"
    if Application.setting and Application.setting.LOG_FILE_NAME:
        log_file_name = Application.setting.LOG_FILE_NAME
    
    # Get log file size
    log_file_size = 10*1024*1024
    if Application.setting and Application.setting.LOG_FILE_SIZE:
        log_file_size = Application.setting.LOG_FILE_SIZE
    
    # Get backup log file count
    log_backup_count = 5
    if Application.setting and Application.setting.LOG_BACKUP_COUNT:
        log_backup_count = Application.setting.LOG_BACKUP_COUNT
        
    logger = setup_logger(log_level, log_file_name, log_file_size, log_backup_count)

    return logger