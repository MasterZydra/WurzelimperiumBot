#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.HTTPCommunication import HTTPConnection
from lxml import etree

class Http(object):
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def getNote(self) -> str:
        """Get the users note"""
        try:
            response, content = self.__http.sendRequest('notiz.php', 'POST')
            self.__http.checkIfHTTPStateIsOK(response)
            content = content.decode('UTF-8')
            my_parser = etree.HTMLParser(recover=True)
            html_tree = etree.fromstring(content, parser=my_parser)

            note = html_tree.find('./body/form/div/textarea[@id="notiztext"]')
            noteText = note.text
            if noteText is None:
                return ''
            return noteText.strip()
        except:
            raise