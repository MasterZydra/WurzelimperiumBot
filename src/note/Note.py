#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.logger.Logger import Logger
from src.note.Http import Http

class Note:
    """This class handles reading from the user notes"""
    _instance = None

    def __new__(self):
        if self._instance is None:
            self._instance = super(Note, self).__new__(self)
            self._instance.__initClass()
        return self._instance
    
    def __initClass(self):
        self.__http = Http()
        self.__content = None
        self.update()

    def update(self) -> bool:
        self.__content = self.__http.get_note()
        return self.__content is not None

    # MARK: Basic functions

    def get_note(self) -> str:
        if self.__content is None:
            self.update()
        return (self.__content or '').replace('\r\n', '\n')

    def get_line(self, starts_with: str) -> str:
        lines = self.get_note().split("\n")
        for line in lines:
            if line.strip() == "":
                continue

            if line.startswith(starts_with):
                return line
        return ''

    # MARK: Extended features
