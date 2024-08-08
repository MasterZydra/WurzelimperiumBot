#!/usr/bin/env python
# -*- coding: utf-8 -*-

class HTTPStateError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class JSONError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class HTTPRequestError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class YAMLError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
