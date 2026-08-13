#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.gardenhouse.Http import Http
from src.logger.Logger import Logger
import time
import random
import re

class GardenHouse:
    def __init__(self):
        self.__http = Http()

    def collect_trophy_points(self) -> bool:
        # Simulate the user opening the garden house
        self.__http.init()

        # Get all trophies
        data = self.__http.get_trophies()
        if data is None:
            return False

        gifts = data.get("gifts", {})
        if not isinstance(gifts, dict):
            return False

        collected_points = 0

        for gift_id, gift_data in gifts.items():
            if not isinstance(gift_data, dict) or gift_data.get("click") is not True:
                continue

            time.sleep(random.choice([0, 3]))

            data = self.__http.click_trophy(str(gift_id))
            if not isinstance(data, dict):
                continue

            msg = data.get("msg", "")
            if not isinstance(msg, str):
                continue

            match = re.search(r"(\d+)", msg)
            if not match:
                continue

            collected_points += int(match.group(1))

        Logger().print(f"Collected {collected_points} points.")

        return True
