#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.HTTPCommunication import HTTPConnection
from src.logger.Logger import Logger

class Http:
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def init(self):
        """Selects ivyhouse returns JSON content"""
        address = f'ajax/ajax.php?do=ivyhouse_init&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except:
            Logger().print_exception('Failed to init ivyhouse')
            return None

    def start_breed(self, slot):
        #slot == type of ivy 1,2,...,7
        """Start ivy and returns JSON content"""
        address = f'ajax/ajax.php?do=ivyhouse_start_breed&slot={slot}&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except:
            Logger().print_exception('Failed to start breed in ivyhouse')
            return None

    def finish_breed(self):
        """Finishes ivy and returns JSON content"""
        address = f'ajax/ajax.php?do=ivyhouse_finish_breed&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except:
            Logger().print_exception('Failed to finish breed in ivyhouse')
            return None

    def remove_pest(self, name, pos):
        #name = pest (Insekten), water (Wassertropfen), mold (Schimmel)
        #pos = 1, weitere?
        address = f'ajax/ajax.php?do=ivyhouse_remove_pest&name={name}&pos={pos}&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except:
            Logger().print_exception('Failed to remove pest in ivyhouse')
            return None

    def set_deco(self, slot, id):
        #slot = 1,2,3,4
        address = f'ajax/ajax.php?do=ivyhouse_set_deco&slot={slot}&id={id}&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except:
            Logger().print_exception(f'Failed to set deco {id} in slot {slot} in ivyhouse')
            return None

    def remove_deco(self, slot):
        #slot = 1,2,3,4
        address = f'ajax/ajax.php?do=ivyhouse_remove_deco&slot={slot}&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except:
            Logger().print_exception(f'Failed to remove deco in slot {slot} in ivyhouse')
            return None

    def set_weather(self, id):
        address = f'ajax/ajax.php?do=ivyhouse_set_weather_item&id={id}&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except:
            Logger().print_exception(f'Failed to set weather {id} in ivyhouse')
            return None

    def remove_weather(self):
        address = f'ajax/ajax.php?do=ivyhouse_remove_weather_item&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except:
            Logger().print_exception('Failed to remove weather in ivyhouse')
            return None

    def buy_item(self, name, slot, amount):
        # name = "deco5"
        # slot = 1
        # amount = 2
        address = f'ajax/ajax.php?do=ivyhouse_buy_shop_item&name={name}&slot={slot}&amount={amount}&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except:
            Logger().print_exception(f'Failed to buy item {name} {amount}x in slot {slot} in ivyhouse')
            return None
