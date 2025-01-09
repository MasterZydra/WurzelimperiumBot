#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.HTTPCommunication import HTTPConnection
from urllib.parse import urlencode

class Http(object):
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def create_new_message_and_return_result(self):
        """Erstellt eine neue Nachricht und gibt deren ID zurück, die für das Senden benötigt wird."""
        try:
            response, content = self.__http.sendRequest('nachrichten/new.php')
            self.__http.checkIfHTTPStateIsOK(response)
            return content
        except:
            raise

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
            response, content = self.__http.sendRequest('nachrichten/new.php', 'POST', parameter)
            self.__http.checkIfHTTPStateIsOK(response)
            return content
        except:
            raise
