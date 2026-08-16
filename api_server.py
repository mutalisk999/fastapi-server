#!/usr/bin/env python
# encoding: utf-8
import getpass
import os
import sys

import uvicorn
from dotenv import load_dotenv

from app import Application
from thread_task import thread_manager
from utils.logger import logger


def sample_task(args, thread):
    """Sample background task. `thread` is the NamedThread instance; polling
    thread.should_stop() supports both per-thread stop and global shutdown."""
    import time
    while not thread.should_stop():
        logger.info("Sample task running...")
        time.sleep(1)
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
    # Prefer CONFIG_PASS from the environment (for systemd/Docker/CI where there
    # is no TTY), falling back to an interactive prompt.
    config_pass = os.environ.get("CONFIG_PASS") or getpass.getpass("input config password: ")
    app = Application.create_app(use_config, config_pass)

    thread_run()

    try:
        # Background threads are stopped gracefully by the app's lifespan on
        # shutdown (see app.lifespan), which uvicorn runs on Ctrl+C / SIGTERM.
        uvicorn.run(
            app,
            host=Application.setting.SERVER_HOST,
            port=Application.setting.SERVER_PORT
        )
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
        thread_manager.stop_all_threads()
    except Exception as e:
        logger.error(f"Error running application: {e}")
        sys.exit(1)
