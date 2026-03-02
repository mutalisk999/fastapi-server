#!/usr/bin/env python
# encoding: utf-8
import getpass
import os
import signal
import sys
import logging

import uvicorn
from dotenv import load_dotenv

from app import Application
from thread_task import thread_manager
from utils.logger import logger


def handle_sig(sig, frame):
    logger.info(f"Caught signal: {sig}, Please wait a few seconds for threads stopping...")
    Application.global_stop = True

    # Use thread manager to stop all threads
    thread_manager.stop_all_threads()
    
    sys.exit(0)


def sample_task(args):
    """Sample background task"""
    import time
    while not Application.global_stop:
        logger.info("Sample task running...")
        time.sleep(5)
    logger.info("Sample task stopped")


def thread_run():
    """Start background threads"""
    # Start sample background thread
    thread_manager.start_thread(
        thread_id="sample_task",
        name="Sample Task",
        function=sample_task,
        args=None
    )


if __name__ == "__main__":
    load_dotenv(".env")
    use_config = os.environ.get("USE_CONFIG", 'default')
    config_pass = getpass.getpass("input config password: ")
    app = Application.create_app(use_config, config_pass)

    # Register signal handlers
    signal.signal(signal.SIGINT, handle_sig)
    signal.signal(signal.SIGTERM, handle_sig)

    thread_run()

    try:
        uvicorn.run(app, host="0.0.0.0", port=7788)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
        handle_sig(signal.SIGINT, None)
    except Exception as e:
        logger.error(f"Error running application: {e}")
        sys.exit(1)
