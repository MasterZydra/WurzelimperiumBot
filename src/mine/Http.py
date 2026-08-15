#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.HTTPCommunication import HTTPConnection
from src.logger.Logger import Logger

class Http:
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def init(self):
        address = f'ajax/ajax.php?do=mine_init&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except:
            Logger().print_exception('Failed to init mine')
            return None

    def finish_worker(self, layer, position):
        address = f'ajax/ajax.php?do=mine_finish&level={layer}&position={position}&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except:
            Logger().print_exception('Failed to finish mine worker')
            return None

    def refill_worker_energy(self, slot, pid, amount):
        address = f'ajax/ajax.php?do=mine_refill&slot={slot}&pid={pid}&amount={amount}&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except:
            Logger().print_exception('Failed to refill mine worker energy')
            return None

    def start_worker(self, setup):
        address = f'ajax/ajax.php?do=mine_harvest&setup={{{setup}}}&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except:
            Logger().print_exception('Failed to start mine worker')
            return None

    def craft_item(self, name):
        address = f'ajax/ajax.php?do=mine_buy_shop_item&name={name}&harvesterslot&dinoslot&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except:
            Logger().print_exception('Failed to craft item')
            return None

    # TODO
    def build_jewel(self):
        # ajax/ajax.php?do=mine_build_jewel&setup=%7B%22slot%22%3A1%2C%22jewel%22%3A%22brooch%22%2C%22jewelType%22%3A%22copper%22%2C%22jewelSlots%22%3A%7B%221%22%3A%22tigereye%22%2C%222%22%3A%22tigereye%22%7D%7D&token=<token>
        # do              mine_build_jewel
        # setup           {"slot":1,"jewel":"brooch","jewelType":"copper","jewelSlots":{"1":"tigereye","2":"tigereye"}}
        # token           <token>
        pass