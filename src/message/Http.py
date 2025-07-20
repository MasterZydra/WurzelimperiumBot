#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.HTTPCommunication import HTTPConnection
from src.logger.Logger import Logger
from urllib.parse import urlencode

class Http:
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def create_new_message_and_return_result(self):
        """Erstellt eine neue Nachricht und gibt deren ID zurück, die für das Senden benötigt wird."""
        try:
            response, content = self.__http.send('nachrichten/new.php')
            self.__http.check_http_state_ok(response)
            return content
        except Exception:
            Logger().print_exception('Failed to create new massge and return result')
            return None

    def send_message_and_return_result(self, msg_id, msg_to, msg_subject, msg_body):
        """Verschickt eine Nachricht mit den übergebenen Parametern."""
        parameter = urlencode({
            'hpc': msg_id,
            'msg_to': msg_to,
            'msg_subject': msg_subject,
            'msg_body': msg_body,
            'msg_send': 'senden'
        })
        try:
            response, content = self.__http.send('nachrichten/new.php', 'POST', parameter)
            self.__http.check_http_state_ok(response)
            return content
        except Exception:
            Logger().print_exception('Failed to send message and return result')
            return None
