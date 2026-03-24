#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
from datetime import date
from src.minigames.pumpkinDigging.Http import Http

class EasterDigging:
    def __init__(self):
        self.__http = Http()

    def is_available(self, page_content: str) -> bool:
        if not self.__check_time_span():
            return False

        if 'id="diggame_bar_img" class="easter"' not in page_content:
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

    def __check_time_span(self) -> bool:
        """Check if today is between 1st march and 30th april"""
        today = date.today()
        start_date = date(today.year, 3, 1)
        end_date = date(today.year, 4, 30)
        return start_date <= today <= end_date