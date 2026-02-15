#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.HTTPCommunication import HTTPConnection
from src.logger.Logger import Logger

class Http:
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def get_info(self):
        address = f'ajax/ajax.php?do=birds_init&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().print_exception('Birds: Failed to get birds info')
            return None

    def start_job(self, jobslot, house_nr):
        """
            jobslot: 1-9
            house_nr: 1-8
        """
        address = f'ajax/ajax.php?do=birds_start_job&jobslot={jobslot}&house={house_nr}&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().print_exception('Birds: Failed to start job')
            return None

    def feed_bird(self, slot):
        """
            slot: 1...9
        """
        address = f'ajax/ajax.php?do=birds_feed_bird&slot={slot}&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().print_exception('Birds: Failed to feed bird')
            return None

    def finish_job(self, slot):
        """
            slot: 1...9
        """
        address = f'ajax/ajax.php?do=birds_finish_job&slot={slot}&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().print_exception(f'Birds: Failed to finish job in slot {slot}')
            return None
        
    def remove_job(self, slot):
        """
            slot: 1...9
        """
        address = f'ajax/ajax.php?do=birds_remove_job&slot={slot}&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().print_exception(f'Birds: Failed to remove job in slot {slot}')
            return None

    def buy_bird(self, house, bird_nr):
        # slot bleibt leer wenn direkt im shop gekauft
        address = f'ajax/ajax.php?do=birds_buy_bird&slot={house}&bird={bird_nr}&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().print_exception(f'Birds: Failed to buy bird {bird_nr} for house {house}')
            return None