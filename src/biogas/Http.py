#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.HTTPCommunication import HTTPConnection
from src.logger.Logger import Logger

class Http(object):
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def get_recycling_center_info(self):
        address = f'ajax/ajax.php?do=biogas_init&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except:
            Logger().print_exception('Failed to get recycling center info')
            return None

    def sell_to_wimp(self, slot):
        address = f'ajax/ajax.php?do=biogas_accept_cart&slot={slot}&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except:
            Logger().print_exception('Biogas: Failed to sell to wimp')
            return None