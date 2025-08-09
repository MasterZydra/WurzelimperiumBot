#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.HTTPCommunication import HTTPConnection
from src.logger.Logger import Logger

class Http:
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def init(self):
        """Selects bonsaigarden returns JSON content(status, data, init, questnr, questData, quest)"""
        try:
            address = f'ajax/ajax.php?do=bonsai_init&token={self.__http.token()}'
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().print_exception('Failed to init bonsai')
            return None

    def buy_and_place(self, item, pack, slot):
        """
        Buys and places an item from the bonsai shop and returns JSON content

        Parameters
        -------------
            slot: 0-10; if 0, item stays in storage
            item:
                bonsais: 1-10 (Mädchenkiefer, Mangrove, Geldbaum, Fichten-Wald, Zypresse, Wacholder, Eiche, ...),
                pots: 11-20 (Einfache Schale, ...),
                scissors: 21-24 (Normale Schere, ...)
            pack:
                1, 5, 10 for bonsais or pots;
                1, 2, 3, 4 for 10, 50, 100, 500 scissors
        """
        address = f'ajax/ajax.php?do=bonsai_buy_item&item={item}&pack={pack}&slot={slot}&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().print_exception('Failed to buy and place bonsai item')
            return None

    def cut(self, slot, sissor, branch):
        """Cuts the branch from the bonsai and returns JSON content(status, data, branchclick, updateMenu)"""
        try:
            address = f'ajax/ajax.php?do=bonsai_branch_click&slot={slot}&' \
                f'scissor={sissor}&cache=%5B{branch}%5D&token={self.__http.token()}'
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().print_exception('Failed to cut bonsai branch')
            return None

    def finish(self, slot):
        """Finishes bonsai to the bonsaigarden and returns JSON content"""
        try:
            address = f'ajax/ajax.php?do=bonsai_finish_breed&slot={slot}&token={self.__http.token()}'
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().print_exception('Failed to finish bonsai')
            return None
