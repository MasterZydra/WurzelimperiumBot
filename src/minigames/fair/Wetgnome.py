#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
from src.minigames.fair.HttpWetgnome import HttpWetgnome

class Wetgnome:
    def __init__(self, data):
        self.__http = HttpWetgnome()
        self.round = 0
        self.game = 0
        self.__set_data(data["data"]["wetgnome"])
        
    def __set_data(self, data):
        self.__data = data
        self.__points = self.__data['data']['points']
        self.round = self.__data['data']['round']
        if "game" in data["data"]:
            self.game = self.__data["data"]["game"]

    def start(self, round):
        if 1 <= round <= 3:
            content = self.__http.start()
            if content is None:
                return None, None
            self.__set_data(content["data"])
        return self.round, self.game

    def select(self, game_id):
        # middle = 51 -> full range between 0 and 102
        x = 48 + random.randint(25, 75)
        x = x + int(game_id[0])

        # middle = 51 -> full range between 0 and 102
        y = 49 + random.randint(25, 75)
        y = y + int(game_id[0])

        content = self.__http.select(x, y)
        if content is None:
            return None
        self.__set_data(content["data"])
        return self.round
    
    def get_points(self):
        return self.__points