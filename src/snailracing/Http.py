#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.HTTPCommunication import HTTPConnection
from src.logger.Logger import Logger

class Http:
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def get_snailracing_info(self):
        address = f'ajax/ajax.php?do=snailracing_init&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except:
            Logger().print_exception('Failed to get snailracing info')
            return None

    def start_bar_production(self, slot, pid):
        """ slot: 1,2,3,4
            pid: 473(red), ???(blue), ..."""
        address = f'ajax/ajax.php?do=snailracing_start_production&slot={slot}&pid={pid}&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except:
            Logger().print_exception('Failed to start bar production')
            return None

    def harvest_bar_production(self, slot):
        """ slot: 1,2,3,4"""
        address = f'ajax/ajax.php?do=snailracing_harvest_production&slot={slot}&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except:
            Logger().print_exception('Failed to harvest bar production')
            return None

    def start_race(self, setup):
        address = f'ajax/ajax.php?do=snailracing_start_race&setup={{{setup}}}&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except:
            Logger().print_exception('Failed to start race')
            return None

    def feed_snail(self, pid, amount): #red bar pid = 473, 
        """pid: snail food"""
        address = f'ajax/ajax.php?do=snailracing_feed_snail&pid={pid}&amount={amount}&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except:
            Logger().print_exception('Failed to feed snail')
            return None

    def finish_race(self):
        address = f'ajax/ajax.php?do=snailracing_get_reward&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except:
            Logger().print_exception('Failed to finish race')
            return None
