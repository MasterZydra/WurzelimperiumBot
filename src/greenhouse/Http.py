#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from src.core.HTTPCommunication import HTTPConnection
from src.logger.Logger import Logger

class Http:
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def init_greenhouse(self):
        """Do all requests when opening the greenhouse"""
        address = f"greenhousetest2.php"
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
        except Exception:
            Logger().print_exception('Failed to init greenhouse')
            return None

        address = f"ajax/greenhouse_ajax.php?op=showhelp"
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            self.__http.get_json_and_check_for_success(content)
        except Exception:
            Logger().print_exception('Failed to init greenhouse')
            return None

        address = f"ajax/greenhouse_ajax.php?op=getrack"
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            self.__http.get_json_and_check_for_success(content)
        except Exception:
            Logger().print_exception('Failed to init greenhouse')
            return None

        address = f"ajax/greenhouse_ajax.php?op=getfields"
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            fields = self.__http.get_json_and_check_for_success(content)
        except Exception:
            Logger().print_exception('Failed to init greenhouse')
            return None

        address = f"ajax/greenhouse_ajax.php?op=getmenu"
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            self.__http.get_json_and_check_for_success(content)
        except Exception:
            Logger().print_exception('Failed to init greenhouse')
            return None

        address = f"ajax/greenhouse_ajax.php?op=gettimedata"
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            self.__http.get_json_and_check_for_success(content)
        except Exception:
            Logger().print_exception('Failed to init greenhouse')
            return None

        return fields
    
    def do_cactus_care(self, activity, fieldID):
        address = f"ajax/greenhouse_ajax.php?activity={activity}&fieldid={fieldID}&op=performactivity"
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return json.loads(content)
        except Exception:
            Logger().print_exception('Failed to do cactus care in greenhouse')
            return None