#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from src.core.HTTPCommunication import HTTPConnection

class Http(object):
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def is_aqua_garden_available(self):
        """Check if aqua garden is available by checking for the achivement"""
        try:
            response, content = self.__http.sendRequest(f'ajax/achievements.php?token={self.__http.token()}')
            self.__http.checkIfHTTPStateIsOK(response)
            content = self.__http.generateJSONContentAndCheckForOK(content)
            result = re.search(r'trophy_54.png\);[^;]*(gray)[^;^class$]*class', content['html'])
            return result == None
        except:
            raise

    def is_bonsai_farm_available(self):
        try:
            response, content = self.__http.sendRequest(f'ajax/ajax.php?do=citymap_init&token={self.__http.token()}')
            self.__http.checkIfHTTPStateIsOK(response)
            content = self.__http.generateJSONContentAndCheckForOK(content)
            if 'bonsai' in content['data']['location']:
                return content['data']['location']['bonsai']['bought'] == 1
            else:
                return False
        except:
            raise

    def is_honey_farm_available(self):
        try:
            response, content = self.__http.sendRequest(f'ajax/ajax.php?do=citymap_init&token={self.__http.token()}')
            self.__http.checkIfHTTPStateIsOK(response)
            content = self.__http.generateJSONContentAndCheckForOK(content)
            if 'bees' in content['data']['location']:
                return content['data']['location']['bees']['bought'] == 1
            else:
                return False
        except:
            raise