#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.HTTPCommunication import HTTPConnection

class Http(object):
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def init_park(self):
        """Activate the park and return JSON content(status, data, init, questnr, questData, quest)"""
        try:
            response, content = self.__http.sendRequest(f'ajax/ajax.php?do=park_init&token={self.__http.token()}')
            self.__http.checkIfHTTPStateIsOK(response)
            return self.__http.generateJSONContentAndCheckForOK(content)
        except:
            raise

    def collect_cash_point(self):
        """collect the rewards from the cashpoint and return JSON content(status, data, clearcashpoint, updateMenu)"""
        try:
            response, content = self.__http.sendRequest(f'ajax/ajax.php?do=park_clearcashpoint&token={self.__http.token()}')
            self.__http.checkIfHTTPStateIsOK(response)
            return self.__http.generateJSONContentAndCheckForOK(content)
        except:
            raise

    def renew_item(self, tile, park_id=1):
        """renew an item on the given tile in the park and return JSON content(status, data, renewitem, updateMenu)"""
        try:
            response, content = self.__http.sendRequest(f'ajax/ajax.php?do=park_renewitem&parkid={park_id}&tile={tile}&token={self.__http.token()}')
            self.__http.checkIfHTTPStateIsOK(response)
            return self.__http.generateJSONContentAndCheckForOK(content)
        except:
            raise