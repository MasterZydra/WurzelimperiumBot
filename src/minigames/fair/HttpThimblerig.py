#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.HTTPCommunication import HTTPConnection

class HttpThimblerig(object):
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def start(self):
        address = f"ajax/ajax.php?do=thimblerig_start&token={self.__http.token()}"
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except:
            raise
    
    def select(self, mug: int):
        """
        @param: mug = 1, 2, 3
        """
        address = f"ajax/ajax.php?do=thimblerig_select&mug={mug}&token={self.__http.token()}"
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except:
            raise