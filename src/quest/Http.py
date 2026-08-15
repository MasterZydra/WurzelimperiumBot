#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.HTTPCommunication import HTTPConnection
from src.logger.Logger import Logger

class Http:
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def get_big_quest_data(self):
        """Returns Data from Yearly Series of Quests"""
        try:
            address = f'ajax/ajax.php?do=bigquest_init&id=3&token={self.__http.token()}'
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            content = self.__http.get_json_and_check_for_ok(content)
            return content['data']
        except Exception:
            Logger().print_exception('Failed to get big quest data')
            return None

    def init_infinity_quest(self):
        adresse = f'ajax/ajax.php?do=infinite_quest_get&token={self.__http.token()}'
        try:
            response, content = self.__http.send(adresse)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().print_exception("Failed to init infinity quest")
            return None

    def send_infinity_quest(self, questnr, product, amount):
        try:
            address =   f'ajax/ajax.php?do=infinite_quest_entry&pid={product}' \
                        f'&amount={amount}&questnr={questnr}&token={self.__http.token()}'
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().print_exception('Failed to send infinity quest')
            return None
