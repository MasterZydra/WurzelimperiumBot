#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from src.core.HTTPCommunication import HTTPConnection

class Http(object):
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def init_greenhouse(self):
        """Do all requests when opening the greenhouse"""
        address = f"greenhousetest2.php"
        try:
            response, content = self.__http.sendRequest(address)
            self.__http.checkIfHTTPStateIsOK(response)
        except:
            raise

        address = f"ajax/greenhouse_ajax.php?op=showhelp"
        try:
            response, content = self.__http.sendRequest(address)
            self.__http.checkIfHTTPStateIsOK(response)
            self.__http.generateJSONContentAndCheckForSuccess(content)
        except:
            raise

        address = f"ajax/greenhouse_ajax.php?op=getrack"
        try:
            response, content = self.__http.sendRequest(address)
            self.__http.checkIfHTTPStateIsOK(response)
            self.__http.generateJSONContentAndCheckForSuccess(content)
        except:
            raise

        address = f"ajax/greenhouse_ajax.php?op=getfields"
        try:
            response, content = self.__http.sendRequest(address)
            self.__http.checkIfHTTPStateIsOK(response)
            fields = self.__http.generateJSONContentAndCheckForSuccess(content)
        except:
            raise

        address = f"ajax/greenhouse_ajax.php?op=getmenu"
        try:
            response, content = self.__http.sendRequest(address)
            self.__http.checkIfHTTPStateIsOK(response)
            self.__http.generateJSONContentAndCheckForSuccess(content)
        except:
            raise

        address = f"ajax/greenhouse_ajax.php?op=gettimedata"
        try:
            response, content = self.__http.sendRequest(address)
            self.__http.checkIfHTTPStateIsOK(response)
            self.__http.generateJSONContentAndCheckForSuccess(content)
        except:
            raise

        return fields
    
    def do_cactus_care(self, activity, fieldID):
        address = f"ajax/greenhouse_ajax.php?activity={activity}&fieldid={fieldID}&op=performactivity"
        try:
            response, content = self.__http.sendRequest(address)
            self.__http.checkIfHTTPStateIsOK(response)
            jContent = json.loads(content)
            return jContent
        except:
            raise