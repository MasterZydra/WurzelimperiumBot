#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
from src.minigames.pumpkinDigging.Http import Http

class PumpkinDigging():

    def __init__(self):
        self.__http = Http()

    def is_available(self) -> bool:
        if not self.__http.game_available():
            return False

        # Check for cooldown
        content = self.__http.init_game()
        return 'map_cooldown' not in content['data']['data'] or content['data']['data']['map_cooldown'] < 0

    def play(self):
        # Select 5 random zones to hit
        zones = random.sample(range(1, 16), 5)

        self.__http.init_game()
        for zone in zones:
            self.__http.hit(zone)
        self.__http.finish_game()