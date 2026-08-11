#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.logger.Logger import Logger
from src.museum.Http import Http

class Museum:
    def __init__(self):
        self.__http = Http()
        self.__data = None
        self.update()

    def update(self):
        self.__set_data(self.__http.init())

    def __set_data(self, content):
        self.__data = content.get("data", {}).get("data", None)

    def collect_points(self):
        if self.__data.get("lastclick_remain", 999999) > 0:
            Logger().print("No points to collect!")
            return False

        content = self.__http.collect_points()

        rewards = content.get("data", {}).get("reward", {}).get("points", "n/a")
        Logger().print(f"Collected {rewards} points.")

        self.__set_data(content)
