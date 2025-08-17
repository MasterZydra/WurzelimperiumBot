#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.HTTPCommunication import HTTPConnection
from src.logger.Logger import Logger

class Http(object):
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def get_info(self):
        try:
            response, content = self.__http.send(f'ajax/ajax.php?do=megafruit_init&token={self.__http.token()}')
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().print_exception('Failed to get megafruit info')
            return None

    def start(self, pid):
        try:
            response, content = self.__http.send(f'ajax/ajax.php?do=megafruit_start&pid={pid}&token={self.__http.token()}')
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().print_exception(f'Failed to start megafruit pid "{pid}"')
            return None

    def care(self, oid):
        try:
            response, content = self.__http.send(f'ajax/ajax.php?do=megafruit_set_object&oid={oid}&token={self.__http.token()}')
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().print_exception(f'Failed to care about megafruit with oid "{oid}"')
            return None

    def harvest(self):
        try:
            response, content = self.__http.send(f'ajax/ajax.php?do=megafruit_harvest&token={self.__http.token()}')
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().print_exception('Failed to harvest megafruit')
            return None