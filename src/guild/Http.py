#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.HTTPCommunication import HTTPConnection

class Http(object):
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def init_guild(self):
        address = f"ajax/ajax.php?do=gildeGetData&&token={self.__http.token()}"
        try:
            response, content = self.__http.sendRequest(address)
            self.__http.checkIfHTTPStateIsOK(response)
            return self.__http.generateJSONContentAndCheckForOK(content)
        except:
            raise

    def collect_lucky_mole(self, guild_id):
        address = f"ajax/ajax.php?do=gilde&action=luckyWurf&id={guild_id}&token={self.__http.token()}"
        try:
            response, content = self.__http.sendRequest(address)
            self.__http.checkIfHTTPStateIsOK(response)
            return self.__http.generateJSONContentAndCheckForOK(content)
        except:
            raise
