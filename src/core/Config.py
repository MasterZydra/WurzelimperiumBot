#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Config:
    """Store the configuration for the WurzelBot environment"""

    # Write log also into std out
    log_to_stdout = False

    _instance = None

    def __new__(self):
        if self._instance is None:
            self._instance = super(Config, self).__new__(self)
        return self._instance