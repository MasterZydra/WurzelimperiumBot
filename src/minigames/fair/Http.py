#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.HTTPCommunication import HTTPConnection
from src.logger.Logger import Logger

class Http:
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def game_available(self) -> bool:
        try:
            response, content = self.__http.send('main.php?page=garden')
            content = content.decode('UTF-8')
            self.__http.update_token_from_content(content)
            self.__http.check_http_state_ok(response)
            return 'id="fair"' in content
        except Exception:
            Logger().exception('Failed to check if fair is available')
            return False

    def init_game(self):
        address = f"ajax/ajax.php?do=fair_init&init=1&token={self.__http.token()}"
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().exception('Failed to init fair game')
            return None

    def craft_ticket(self):
        address = f"ajax/ajax.php?do=fair_craftticket&token={self.__http.token()}"
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().exception('Failed to craft tickets for fair game')
            return None
    
    def pay_ticket(self, type):
        """
        @param: type = wetgnome, thimblerig
        """
        address = f"ajax/ajax.php?do=fair_payticket&type={type}&token={self.__http.token()}"
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().exception('Failed to pay tickets for fair game')
            return None