#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.HTTPCommunication import HTTPConnection

class Http(object):
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def get_info_from_stats(self, info):
        return self.__http.getInfoFromStats(info)

    def get_big_quest_data(self):
        """Returns Data from Yearly Series of Quests"""
        try:
            address = f'ajax/ajax.php?do=bigquest_init&id=3&token={self.__http.token()}'
            response, content = self.__http.sendRequest(address)
            self.__http.checkIfHTTPStateIsOK(response)
            jContent = self.__http.generateJSONContentAndCheckForOK(content)
            return jContent['data']
        except:
            pass