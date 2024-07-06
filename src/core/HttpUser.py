#!/usr/bin/env python
# -*- coding: utf-8 -*-

import html, re
from src.core.HTTPCommunication import HTTPConnection

class Http(object):
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def load_data(self, data_type="UserData"):
        return self.__http.readUserDataFromServer(data_type)

    def get_info_from_stats(self, info):
        return self.__http.getInfoFromStats(info)

    def get_user_id(self):
        return self.__http.get_user_id()

    def check_mail_confirmed(self):
        """Check if mail address is confirmed"""
        try:
            response, content = self.__http.sendRequest('nutzer/profil.php')
            self.__http.checkIfHTTPStateIsOK(response)
            result = re.search('Unbestätigte Email:', html.unescape(str(content)))
            return result == None
        except:
            raise

