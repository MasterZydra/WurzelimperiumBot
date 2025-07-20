#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.minigames.fair.HttpThimblerig import HttpThimblerig

class Thimblerig:
    def __init__(self, data):
        self.__http = HttpThimblerig()
        self.round = 0
        self.mug = 0
        self.__set_data(data["data"]["thimblerig"])
        
    def __set_data(self, data):
        self.__data = data
        self.__points = self.__data['data']['points']
        self.round = self.__data['data']['round']
        if "game" in data["data"]:
            self.mug = self.__data["data"]["game"]["mug"]

    def start(self, round):
        if 1 <= round <= 3:
            content = self.__http.start()
            if content is None:
                return None
            self.__set_data(content["data"])
        return self.round

    def select(self):
        if 1 <= self.mug <= 3:
            content = self.__http.select(self.mug)
            if content is None:
                return None
            self.__set_data(content["data"])
        return self.round
    
    def get_points(self):
        return self.__points