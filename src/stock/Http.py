#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.HTTPCommunication import HTTPConnection
from src.logger.Logger import Logger

class Http:
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def get_inventory(self):
        """Determines the plants in stock"""
        try:
            address = f'ajax/updatelager.php?all=1&sort=1&type=honey&token={self.__http.token()}'
            response, content = self.__http.send(address, 'POST')
            self.__http.check_http_state_ok(response)
            jContent = self.__http.get_json_and_check_for_ok(content)
            return jContent['produkte']
        except Exception:
            Logger().print_exception("Failed to get stock inventory")
            return None