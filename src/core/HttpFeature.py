#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from src.core.HTTPCommunication import HTTPConnection
from src.core.HttpUser import Http as HttpUser
from src.logger.Logger import Logger

class Http:
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()
        self.__httpUser = HttpUser()

    def is_aqua_garden_available(self) -> bool:
        """Check if aqua garden is available by checking for the achivement"""
        try:
            response, content = self.__http.send(f'ajax/achievements.php?token={self.__http.token()}')
            self.__http.check_http_state_ok(response)
            content = self.__http.get_json_and_check_for_ok(content)
            result = re.search(r'trophy_54.png\);[^;]*(gray)[^;^class$]*class', content['html'])
            return result == None
        except Exception:
            Logger().print_exception('Failed to check if aqua garden is available')
            return False

    def get_citymap_data(self) -> dict|None:
        try:
            response, content = self.__http.send(f'ajax/ajax.php?do=citymap_init&token={self.__http.token()}')
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().print_exception('Failed to get citymap data')
            return None

    def is_greenhouse_available(self) -> bool:
        try:
            cactus_quest = self.__httpUser.get_info_from_stats("CactusQuest")
            if cactus_quest is None:
                return False
            return cactus_quest > 0
        except Exception:
            Logger().print_exception('Failed to check if greenhouse is available')
            return False
