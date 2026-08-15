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

    def start_production(self, setup):
        address = f'ajax/ajax.php?do=biogas_production_start&setup={{{setup}}}&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except:
            Logger().print_exception('Failed to start biogas production')
            return None

    def harvest_production(self, material_type, slot):
        address = f'ajax/ajax.php?do=biogas_production_harvest&type={material_type}&slot={slot}&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except:
            Logger().print_exception('Failed to harvest biogas production')
            return None

    def buy_item(self, item_name, item_slot = 0, item_amount = 1):
        address = f'ajax/ajax.php?do=biogas_buy_shop_item&name={item_name}&slot={item_slot}&amount={item_amount}&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except:
            Logger().print_exception('Failed to buy biogas item')
            return None
