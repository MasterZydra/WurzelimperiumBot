#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.HTTPCommunication import HTTPConnection
from src.logger.Logger import Logger
from lxml import etree

class Http:
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def get_note(self) -> (str | None):
        """Get the users note"""
        try:
            response, content = self.__http.send('notiz.php', 'POST')
            self.__http.check_http_state_ok(response)
            content = content.decode('UTF-8')
            my_parser = etree.HTMLParser(recover=True)
            html_tree = etree.fromstring(content, parser=my_parser)
            if html_tree is None:
                return ''

            note = html_tree.find('./body/form/div/textarea[@id="notiztext"]')
            note_text = note.text
            if note_text is None:
                return ''
            return note_text.strip()
        except Exception:
            Logger().print_exception('Failed to get note')
            return None