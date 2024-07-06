#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Config(object):
    """Store the configuration for the WurzelBot environment"""

    # Is bot running in development environment?
    # This mode will show more details e.g. not hidding exception message
    isDevMode = False

    _instance = None

    def __new__(self):
        if self._instance is None:
            self._instance = super(Config, self).__new__(self)
        return self._instance