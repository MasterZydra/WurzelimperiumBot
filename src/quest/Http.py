#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.HTTPCommunication import HTTPConnection
from src.logger.Logger import Logger

class Http:
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def get_big_quest_data(self):
        """Returns Data from Yearly Series of Quests"""
        try:
            address = f'ajax/ajax.php?do=bigquest_init&id=3&token={self.__http.token()}'
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            jContent = self.__http.get_json_and_check_for_ok(content)
            return jContent['data']
        except Exception:
            Logger().print_exception('Failed to get big quest data')
            return None