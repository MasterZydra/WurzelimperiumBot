#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.HTTPCommunication import HTTPConnection

class Http(object):
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def get_inventory(self):
        """Determines the plants in stock"""
        try:
            address = f'ajax/updatelager.php?all=1&sort=1&type=honey&token={self.__http.token()}'
            response, content = self.__http.sendRequest(address, 'POST')
            self.__http.checkIfHTTPStateIsOK(response)
            jContent = self.__http.generateJSONContentAndCheckForOK(content)
            return jContent['produkte']
        except:
            pass