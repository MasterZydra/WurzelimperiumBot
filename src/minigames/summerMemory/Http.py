#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.HTTPCommunication import HTTPConnection
from src.logger.Logger import Logger

class Http:
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def init_game(self):
        try:
            response, content = self.__http.send(f'ajax/ajax.php?do=memory_init&token={self.__http.token()}')
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().print_exception('Failed to init summer memory')
            return None

    def flip(self, position: int):
        try:
            response, content = self.__http.send(f'ajax/ajax.php?do=memory_flip&position={position}&token={self.__http.token()}')
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().print_exception('Failed to flip card in summer memory')
            return None

    def exchange(self):
        try:
            response, content = self.__http.send(f'ajax/ajax.php?do=memory_buy_shop&id=5&token={self.__http.token()}')
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().print_exception('Failed to exchange points in summer memory')
            return None
