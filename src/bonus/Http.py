#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.HTTPCommunication import HTTPConnection

class Http(object):
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def get_daily_login_bonus(self, day):
        """@param day: string (day of daily bonus)"""
        try:
            address = f'ajax/ajax.php?do=dailyloginbonus_getreward&day={str(day)}&token={self.__http.token()}'
            response, content = self.__http.sendRequest(address)
            self.__http.checkIfHTTPStateIsOK(response)
            return self.__http.generateJSONContentAndCheckForOK(content)
        except:
            pass
    
    def read_user_data(self):
        return self.__http.readUserDataFromServer(data_type="dailyloginbonus")['dailyloginbonus']