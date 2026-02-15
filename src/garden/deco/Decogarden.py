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

    def collect(self):
        self.__http.init_decogarden_2()
        content = self.__http.collect_decogarden_2()
        collected = content.get('data', {}).get('reward', 'None')
        Logger().print(collected)
