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
            return 'id="calendar" class="xmas long"' in content
        except Exception:
            Logger().print_exception('Failed to check if advent calendar is available')
            return False

    def init_game(self):
        try:
            response, content = self.__http.send(f'ajax/ajax.php?do=calendar_init&token={self.__http.token()}')
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().print_exception('Failed to init advent calender')
            return None

    def open(self, field: int):
        try:
            response, content = self.__http.send(f'ajax/ajax.php?do=calendar_open&field={field}&token={self.__http.token()}')
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().print_exception('Failed to open advent calender')
            return None
