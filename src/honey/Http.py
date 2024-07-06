#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.HTTPCommunication import HTTPConnection

class Http(object):
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def get_honey_farm_info(self):
        address = f'ajax/ajax.php?do=bees_init&token={self.__http.token()}'
        try:
            response, content = self.__http.sendRequest(address)
            self.__http.checkIfHTTPStateIsOK(response)
            jContent = self.__http.generateJSONContentAndCheckForOK(content)
            return jContent
        except:
            raise
        
    def pour_honey(self):
        address = f'ajax/ajax.php?do=bees_fill&token={self.__http.token()}'
        try:
            response, content = self.__http.sendRequest(address)
            self.__http.checkIfHTTPStateIsOK(response)
            jContent = self.__http.generateJSONContentAndCheckForOK(content)
            return jContent
        except:
            raise 

    def change_hive_type(self, hive, pid): 
        address = f'ajax/ajax.php?do=bees_changehiveproduct&id={hive}' \
                  f'&pid={pid}&token={self.__http.token()}'
        try:
            response, content = self.__http.sendRequest(address)
            self.__http.checkIfHTTPStateIsOK(response)
            jContent = self.__http.generateJSONContentAndCheckForOK(content)
            return jContent
        except:
            raise

    def send_bees(self, tour):
        """parameters: tour: 1 = 2h, 2 = 8h, 3 = 24h"""
        address = f'ajax/ajax.php?do=bees_startflight_all&tour={tour}&token={self.__http.token()}'
        try:
            response, content = self.__http.sendRequest(address)
            self.__http.checkIfHTTPStateIsOK(response)
            jContent = self.__http.generateJSONContentAndCheckForOK(content)
            return jContent
        except:
            raise