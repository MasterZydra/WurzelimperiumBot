#!/usr/bin/env python
# -*- coding: utf-8 -

import logging
from pathlib import Path
from src.core.Config import Config

class Logger:
    _instance = None

    def __new__(self):
        if self._instance is None:
            self._instance = super(Logger, self).__new__(self)
            self._instance.__initClass()
        return self._instance

    def __initClass(self):
        Path('logs').mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger('Bot')
        handler = logging.FileHandler('logs/wurzelbot.log', 'a', 'utf-8')
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        if Config().log_to_stdout:
            self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(logging.INFO)

    def print_exception(self, message: str):
        """Print and log as exception"""
        self.exception(message)
        if not Config().log_to_stdout:
            print(message)

    def exception(self, message):
        """Logs the given message followed by the stack trace of the raised exception"""
        self.logger.exception(message)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def print(self, message: str):
        """Print and log as info"""
        self.info(message)
        if not Config().log_to_stdout:
            print(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def print_error(self, message: str):
        """Print and log as error"""
        self.error(message)
        if not Config().log_to_stdout:
            print(message)
