#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from src.core.HTTPCommunication import HTTPConnection
from src.core.HttpUser import Http as HttpUser

class Http(object):
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()
        self.__httpUser = HttpUser()

    def is_aqua_garden_available(self):
        """Check if aqua garden is available by checking for the achivement"""
        try:
            response, content = self.__http.send(f'ajax/achievements.php?token={self.__http.token()}')
            self.__http.check_http_state_ok(response)
            content = self.__http.get_json_and_check_for_ok(content)
            result = re.search(r'trophy_54.png\);[^;]*(gray)[^;^class$]*class', content['html'])
            return result == None
        except:
            raise

    def is_bonsai_farm_available(self):
        try:
            response, content = self.__http.send(f'ajax/ajax.php?do=citymap_init&token={self.__http.token()}')
            self.__http.check_http_state_ok(response)
            content = self.__http.get_json_and_check_for_ok(content)
            if 'bonsai' in content['data']['location']:
                return content['data']['location']['bonsai']['bought'] == 1
            else:
                return False
        except:
            raise

    def is_honey_farm_available(self):
        try:
            response, content = self.__http.send(f'ajax/ajax.php?do=citymap_init&token={self.__http.token()}')
            self.__http.check_http_state_ok(response)
            content = self.__http.get_json_and_check_for_ok(content)
            if 'bees' in content['data']['location']:
                return content['data']['location']['bees']['bought'] == 1
            else:
                return False
        except:
            raise

    def is_greenhouse_available(self):
        try:
            cactus_quest = self.__httpUser.get_info_from_stats("CactusQuest")
            if cactus_quest > 0:
                return True
            return False
        except:
            raise