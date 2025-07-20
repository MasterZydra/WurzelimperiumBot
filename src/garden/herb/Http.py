#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.HTTPCommunication import HTTPConnection
from src.logger.Logger import Logger
import json

class Http:
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def harvest(self):
        address = f'ajax/ajax.php?do=gardenHarvestAll&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return json.loads(content)
        except Exception:
            Logger().print_exception('Failed to init herb garden')
            return None

    def load_data(self):
        address = f"ajax/ajax.php?do=herb&action=getGarden&token={self.__http.token()}"
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().print_exception('Failed to load data of herb garden')
            return None

    def remove_weed(self):
        address = f"ajax/ajax.php?do=herb&action=removeHerbWeed&token={self.__http.token()}"
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().print_exception('Failed to remove weed in herb garden')
            return None

    def exchange(self, plantID):
        address = f"ajax/ajax.php?do=herbEvent&action=exchange&plantid={plantID}&token={self.__http.token()}"
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().print_exception('Failed to exchange in herb garden')
            return None
