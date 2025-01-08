#!/usr/bin/env python
# encoding: utf-8
import getpass
import os
import signal
import sys

import uvicorn
from dotenv import load_dotenv

from app import Application


def handle_sig(sig, frame):
    print("Caught Sig: %d, Please wait a few seconds for threads stopping..." % sig)
    Application.global_stop = True

    for k, v in Application.thread_running_dict.items():
        v.join()
        print("thread: {} stopped!".format(k))
    sys.exit(0)


def thread_run():
    pass


if __name__ == "__main__":
    load_dotenv(".env")
    use_config = os.environ.get("USE_CONFIG", 'default')
    config_pass = getpass.getpass("input config password: ")
    app = Application.create_app(use_config, config_pass)

    thread_run()

    uvicorn.run(app, host="0.0.0.0", port=7788)
    # out of uvicorn event loop
    # pretending we catch the interrupt signal and then stop all biz threads
    handle_sig(signal.SIGINT, None)
