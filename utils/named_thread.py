#!/usr/bin/env python
# encoding: utf-8
import threading


class NamedThread(threading.Thread):
    def __init__(self, thread_id, name, function_ptr, args=None):
        threading.Thread.__init__(self)
        self.args = args
        self.thread_id = thread_id
        self.name = name
        self.function_ptr = function_ptr

    def run(self):
        self.function_ptr(self.args)
