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

    def init_garden_shed(self):
        try:
            response, content = self.__http.sendRequest(f'ajax/ajax.php?do=houseInit&token={self.__http.token()}')
            self.__http.checkIfHTTPStateIsOK(response)
            self.__http.generateJSONContentAndCheckForOK(content)
        except:
            raise

    def open_trophy_case(self):
        try:
            response, content = self.__http.sendRequest('ajax/gettrophies.php?category=giver')
            self.__http.checkIfHTTPStateIsOK(response)
            self.__http.generateJSONContentAndCheckForOK(content)
        except:
            raise

    def collect_bonus_items(self):
        try:
            response, content = self.__http.sendRequest('ajax/presentclick.php', 'POST')
            self.__http.checkIfHTTPStateIsOK(response)
            return self.__http.generateJSONContentAndCheckForOK(content)
        except:
            raise
    
    def init_guild(self):
        return self.__http.init_guild()

    def collect_lucky_mole(self, guild_id):
        return self.__http.collect_lucky_mole(guild_id)