#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.User import User
from src.garden.deco.Http import Http
from src.logger.Logger import Logger

class Decogarden1():
    """Wrapper for the Decogarden 1"""

    def __init__(self):
        self.__http = Http()

    def collect(self) -> bool:
        data = self.__http.init_decogarden_1()
        if data is None:
            return True

        if User().is_premium_active():
            content = self.__http.collect_decogarden_1_premium()
            collected = content.get('message', 'Collected nothing!')
            Logger().print(collected)
            return True

        for pos in data['grid']:
            item = data['grid'][pos]

            if not 'bonus' in item or item['bonus'] == '':
                continue
            if item['nextclick'] != 0:
                continue

            content = self.__http.collect_decogarden_1_item(pos)
            Logger().print(content.get('message', 'Collected nothing!').replace('&nbsp;', ' '))
        return True

class Decogarden2():
    """Wrapper for the Decogarden 2"""

    def __init__(self):
        self.__http = Http()
        self.__data = self.__http.init_decogarden_2()

    def collect(self):
        if self.__check_for_points_deco():
            content = self.__http.collect_decogarden_2()
            collected = content.get('data', {}).get('reward', 'None')
            Logger().print(collected)

    def __check_for_points_deco(self):
        placed_deco = self.__data.get("data", {}).get("data", {}).get("data_grid", {})
        if placed_deco == []: return False # no decoration placed
        for field, attributes in placed_deco.items():
            if attributes.get("nextclick", 0):
                return True
        return False

