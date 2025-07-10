#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.HTTPCommunication import HTTPConnection

class Http:
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def init_guild(self):
        address = f"ajax/ajax.php?do=gildeGetData&&token={self.__http.token()}"
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            raise

    def collect_lucky_mole(self, guild_id):
        address = f"ajax/ajax.php?do=gilde&action=luckyWurf&id={guild_id}&token={self.__http.token()}"
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            raise
