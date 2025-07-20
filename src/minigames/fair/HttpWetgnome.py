#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.HTTPCommunication import HTTPConnection
from src.logger.Logger import Logger

class HttpWetgnome:
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def start(self):
        address = f"ajax/ajax.php?do=wetgnome_start&token={self.__http.token()}"
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().print_exception('Failed to start wet gnome game')
            return None

    def select(self, x, y):
        """
        @param: x = game_id + position, y = game_id + position
        """
        address = f"ajax/ajax.php?do=wetgnome_select&x={x}&y={y}&token={self.__http.token()}"
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().print_exception('Failed to select in wet gnome game')
            return None
