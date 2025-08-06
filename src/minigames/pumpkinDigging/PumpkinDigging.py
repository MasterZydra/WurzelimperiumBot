#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
from src.minigames.pumpkinDigging.Http import Http

class PumpkinDigging:
    def __init__(self):
        self.__http = Http()

    def is_available(self, page_content: str) -> bool:
        if 'id="diggame_bar_img" class="autumn"' not in page_content:
            return False

        # Check for cooldown
        content = self.__http.init_game()
        if content is None:
            return False
        return 'map_cooldown' not in content['data']['data'] or content['data']['data']['map_cooldown'] < 0

    def play(self) -> bool:
        # Select 5 random zones to hit
        zones = random.sample(range(1, 16), 5)

        if self.__http.init_game() is None:
            return False
        for zone in zones:
            if self.__http.hit(zone) is None:
                return False
        return self.__http.finish_game() is not None