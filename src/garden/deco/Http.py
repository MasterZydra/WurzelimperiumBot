#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from src.core.HTTPCommunication import HTTPConnection
from src.logger.Logger import Logger

class Http(object):
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def init_decogarden_1(self):
        try:
            response, content = self.__http.send('ajax/decogardenajax.php?do=getGarden')
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().print_exception('Failed to init deco garden 1')
            return None

    def collect_decogarden_1_item(self, pos: str):
        try:
            response, content = self.__http.send(f'ajax/decogardenajax.php?do=collectItem&pos={pos}')
            self.__http.check_http_state_ok(response)
            return json.loads(content)
        except Exception:
            Logger().print_exception(f'Failed to collect deco garden 1 item at pos {pos}')
            return None

    def collect_decogarden_1_premium(self):
        try:
            response, content = self.__http.send('ajax/decogardenajax.php?do=premiumCollector')
            self.__http.check_http_state_ok(response)
            return json.loads(content)
        except Exception:
            Logger().print_exception('Failed to collect deco garden 1 with premium collector')
            return None

    def init_decogarden_2(self):
        try:
            response, content = self.__http.send(f'ajax/ajax.php?do=decogarden2_init&token={self.__http.token()}')
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().print_exception('Failed to init deco garden 2')
            return None

    def collect_decogarden_2(self):
        try:
            response, content = self.__http.send(f'ajax/ajax.php?do=decogarden2_collect_all_items&token={self.__http.token()}')
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().print_exception('Failed to collect deco garden 2')
            return None