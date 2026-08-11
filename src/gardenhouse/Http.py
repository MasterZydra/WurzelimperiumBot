#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.HTTPCommunication import HTTPConnection
from src.logger.Logger import Logger
from urllib.parse import urlencode

class Http:
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def init(self):
        address = f'ajax/ajax.php?do=houseInit&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except:
            Logger().print_exception('Failed to init garden house')
            return None

    def get_trophies(self):
        address = 'ajax/gettrophies.php?category=giver'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except:
            Logger().print_exception('Failed to get trophies')
            return None

    def click_trophy(self, trophy_id: str):
        try:
            parameter = urlencode({
                'item': trophy_id,
                'token': self.__http.token(),
            })
            header = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
            response, content = self.__http.send('ajax/presentclick.php', 'POST', parameter, header)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except:
            Logger().print_exception('Failed to collect trophy points')
            return None
