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
            return 'id="diggame_bar_img" class="autumn"' in content
        except Exception:
            Logger().exception('Failed to check if pumpkin digging is available')
            return False

    def init_game(self):
        try:
            response, content = self.__http.send(f'ajax/ajax.php?do=diggame_init&token={self.__http.token()}')
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().exception('Failed to init pumpkin digging')
            return None

    def hit(self, zone: int):
        try:
            response, content = self.__http.send(f'ajax/ajax.php?do=diggame_map_hit&zone={zone}&token={self.__http.token()}')
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().exception('Failed to hit zone in pumpkin digging')
            return None

    def finish_game(self):
        try:
            response, content = self.__http.send(f'ajax/ajax.php?do=diggame_map_finish&option=1&token={self.__http.token()}')
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().exception('Failed to finish pumpkin digging')
            return None