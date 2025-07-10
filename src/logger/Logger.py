#!/usr/bin/env python
# -*- coding: utf-8 -

import logging

class Logger:
    _instance = None

    def __new__(self):
        if self._instance is None:
            self._instance = super(Logger, self).__new__(self)
            self._instance.__initClass()
        return self._instance

    def __initClass(self):
        self.logger = logging.getLogger('Bot')
        # TODO Add option print output for runs in pipeline without persistent storage
        # handler = logging.StreamHandler()
        handler = logging.FileHandler('logs/wurzelbot.log', 'a', 'utf-8')
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def exception(self, message):
        """Logs the given message followed by the stack trace of the raised exception"""
        self.logger.exception(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)
