#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.HTTPCommunication import HTTPConnection
from src.core.HttpUser import Http as HttpUser

class Http:
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()
        self.__httpUser = HttpUser()

    def get_daily_login_bonus(self, day):
        """@param day: string (day of daily bonus)"""
        try:
            address = f'ajax/ajax.php?do=dailyloginbonus_getreward&day={str(day)}&token={self.__http.token()}'
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except:
            pass

    def read_user_data(self):
        return self.__httpUser.load_data("dailyloginbonus")['dailyloginbonus']

    def init_garden_shed(self):
        try:
            response, content = self.__http.send(f'ajax/ajax.php?do=houseInit&token={self.__http.token()}')
            self.__http.check_http_state_ok(response)
            self.__http.get_json_and_check_for_ok(content)
        except:
            raise

    def open_trophy_case(self):
        try:
            response, content = self.__http.send('ajax/gettrophies.php?category=giver')
            self.__http.check_http_state_ok(response)
            self.__http.get_json_and_check_for_ok(content)
        except:
            raise

    def collect_bonus_items(self):
        try:
            response, content = self.__http.send('ajax/presentclick.php', 'POST')
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except:
            raise
