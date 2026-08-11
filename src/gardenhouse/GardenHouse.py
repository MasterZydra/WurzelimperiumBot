#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.gardenhouse.Http import Http
from src.logger.Logger import Logger
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
            if isinstance(gift_data, dict) and gift_data.get("click") is True:
                data = self.__http.click_trophy(str(gift_id))
                if isinstance(data, dict):
                    msg = data.get("msg", "")
                    if isinstance(msg, str):
                        match = re.search(r"(\d+)", msg)
                        if match:
                            collected_points += int(match.group(1))

        Logger().print(f"Collected {collected_points} points.")

        return True
