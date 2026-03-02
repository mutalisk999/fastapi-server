#!/usr/bin/env python
# encoding: utf-8
import threading
from utils.logger import logger


class NamedThread(threading.Thread):
    def __init__(self, thread_id, name, function_ptr, args=None):
        threading.Thread.__init__(self)
        self.args = args
        self.thread_id = thread_id
        self.name = name
        self.function_ptr = function_ptr
        self.status = "created"  # created, running, completed, error
        self.error = None

    def run(self):
        try:
            self.status = "running"
            logger.info(f"Thread {self.name} (ID: {self.thread_id}) started")
            self.function_ptr(self.args)
            self.status = "completed"
            logger.info(f"Thread {self.name} (ID: {self.thread_id}) completed successfully")
        except Exception as e:
            self.status = "error"
            self.error = str(e)
            logger.error(f"Thread {self.name} (ID: {self.thread_id}) failed with error: {e}")

    def get_status(self):
        """Get the current status of the thread"""
        return self.status

    def get_error(self):
        """Get the error message if the thread failed"""
        return self.error
