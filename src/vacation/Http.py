#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.HTTPCommunication import HTTPConnection
from src.logger.Logger import Logger

class Http:
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def get_info(self):
        address = f'ajax/ajax.php?do=vacation_init&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().print_exception('Failed to get vacation info')
            return None

    def book_location(self, id, setup):
        address = f'ajax/ajax.php?do=vacation_book_location&id={id}&setup={setup}&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().print_exception('Failed to book location')
            return None

    def refill_location(self, id, pid, amount):
        address = f'ajax/ajax.php?do=vacation_refill_location&id={id}&pid={pid}&amount={amount}&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().print_exception('Failed to refill location')
            return None

    def harvest_location_slot(self, id, slot):
        address = f'ajax/ajax.php?do=vacation_harvest_location_slot&id={id}&slot={slot}&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().print_exception('Failed to harvest location')
            return None

    def buy_item(self, name, amount, slot=None):
        #slot bleibt leer wenn direkt im shop gekauft
        address = f'ajax/ajax.php?do=vacation_buy_shop_item&name={name}&slot={slot}&amount={amount}&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().print_exception('Failed to buy vacation item')
            return None
