#!/usr/bin/env python
# encoding: utf-8
from typing import Dict, Optional, Callable, Any
from utils.named_thread import NamedThread
from app import Application
from utils.logger import logger


class ThreadManager:
    """Thread manager to handle background threads"""
    
    def __init__(self):
        self.threads: Dict[str, NamedThread] = {}
    
    def start_thread(self, thread_id: str, name: str, function: Callable, args: Any = None) -> bool:
        """Start a new thread"""
        try:
            if thread_id in self.threads:
                logger.warning(f"Thread with ID {thread_id} already exists")
                return False
            
            thread = NamedThread(thread_id, name, function, args)
            thread.daemon = True  # Make thread daemon so it doesn't block shutdown
            thread.start()
            self.threads[thread_id] = thread
            Application.thread_running_dict[thread_id] = thread
            logger.info(f"Started thread: {name} (ID: {thread_id})")
            return True
        except Exception as e:
            logger.error(f"Error starting thread: {e}")
            return False
    
    def stop_thread(self, thread_id: str) -> bool:
        """Stop a thread"""
        try:
            if thread_id not in self.threads:
                logger.warning(f"Thread with ID {thread_id} does not exist")
                return False
            
            thread = self.threads[thread_id]
            logger.info(f"Stopping thread: {thread.name} (ID: {thread_id})")
            # Set global stop flag
            Application.global_stop = True
            # Wait for thread to stop
            thread.join(timeout=5)
            if thread.is_alive():
                logger.warning(f"Thread {thread_id} did not stop within timeout")
            else:
                logger.info(f"Thread {thread_id} stopped successfully")
            
            # Remove from dictionaries
            del self.threads[thread_id]
            if thread_id in Application.thread_running_dict:
                del Application.thread_running_dict[thread_id]
            
            return True
        except Exception as e:
            logger.error(f"Error stopping thread: {e}")
            return False
    
    def get_thread_status(self, thread_id: str) -> Optional[str]:
        """Get the status of a thread"""
        if thread_id not in self.threads:
            return None
        return self.threads[thread_id].get_status()
    
    def get_all_threads(self) -> Dict[str, NamedThread]:
        """Get all threads"""
        return self.threads
    
    def stop_all_threads(self):
        """Stop all threads"""
        logger.info("Stopping all threads")
        for thread_id in list(self.threads.keys()):
            self.stop_thread(thread_id)
        logger.info("All threads stopped")


# Create a global thread manager instance
thread_manager = ThreadManager()