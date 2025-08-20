#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.logger.Logger import Logger
from src.megafruit.Http import Http
from src.megafruit.MegafruitData import Mushroom, Care_OID, Care, is_fertilize_care_item, is_light_care_item, is_water_care_item, get_care_item_price
from src.core.User import User

class Megafruit:
    def __init__(self):
        self.__http = Http()
        self.__data = None
        self.update()

    def update(self) -> bool:
        data = self.__http.get_info()
        if data is None:
            return False

        return self.__set_data(data)

    def __set_data(self, content: dict) -> bool:
        self.__data = content.get("data", None)
        return self.__data is not None

    # MARK: Base functions

    def start(self, plant: Mushroom = 0) -> bool:
        if self.is_planted():
            return True

        if not plant:
            return False

        Logger().debug(f'Start megafruit {plant}')
        pid = plant.value

        data = self.__http.start(pid)
        if data is None:
            return False

        return self.__set_data(data)

    def harvest(self) -> bool:
        if self.get_remaining_time() >= 0:
            return True

        data = self.__http.harvest()
        if data is None:
            return False
        return self.__set_data(data)

    def care(self, oid: int) -> bool:
        if is_water_care_item(oid):
            return self.__care(Care.WATER, oid)

        if is_light_care_item(oid):
            return self.__care(Care.LIGHT, oid)

        if is_fertilize_care_item(oid):
            return self.__care(Care.FERTILIZE, oid)

        Logger().debug(f'Unhandled care OID {oid}')
        return False

    # MARK: Helpers

    def is_planted(self) -> bool:
        return bool(self.__data.get('entry', 0))

    def get_remaining_time(self) -> int:
        return self.__data.get('remain', 0)

    def get_spores(self) -> int:
        return int(self.__data['count'])

    def get_unlocked_care_items(self) -> list:
        items = [ Care_OID.WATER_1.value ]
        if 'data' not in self.__data or 'unlock' not in self.__data['data']:
            return items
        for oid in self.__data['data']['unlock']:
            items.append(int(oid))
        return items

    def get_best_care_item(self, item_type: str, allowed_care_item_prices: list = ['money', 'coins', 'fruits']) -> int|None:
        """
        item_type: 'water', 'light', 'fertilize'
        """
        care_items = self.get_unlocked_care_items()
        best_item = None
        for item in care_items:
            # Check if current item is the given type
            if item_type == 'water' and not is_water_care_item(item):
                continue
            if item_type == 'light' and not is_light_care_item(item):
                continue
            if item_type == 'fertilize' and not is_fertilize_care_item(item):
                continue

            # Get price for the item
            price = get_care_item_price(item)
            if price is None:
                continue
            price, unit = price

            # Check if the unit of price is allowed
            if unit not in allowed_care_item_prices:
                continue

            # Check is user has enough money, fruits or coins to pay for item
            if (unit == 'money' and User().get_bar() >= price) or \
                (unit == 'fruits' and self.get_spores() >= price) or \
                (unit == 'coins' and User().get_coins() >= price):
                best_item = item

        return best_item

    def __care(self, care_name: Care, oid) -> bool:
        """
        Example
        -------
        "entry": {
            "pid": "272",
            "points": "244",
            "data": {
                "used": {
                    "water": {
                        "oid": 3,
                        "time": 1705427331,
                        "duration": 28800,
                        "remain": 28800
                    }
                }
            },
            "createdate": "1705427210"
        },
        "fruit_percent": 10,
        "remain": 604679,
        """

        entry = self.__data.get('entry', None)
        if entry is None:
            return False

        # Check if care item is still in use
        if not entry.get('data', {}) == "":
            if entry.get('data', {}).get('used', {}).get(care_name.value, {}).get('remain', 0) > 0:
                return True

        match care_name:
            case Care.WATER:
                Logger().print('Care megafruit with water')
            case Care.LIGHT:
                Logger().print('Care megafruit with light')
            case Care.FERTILIZE:
                Logger().print('Care megafruit with fertilizer')

        data = self.__http.care(oid)
        return self.__set_data(data)
