#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from src.HTTPCommunication import HTTPConnection

class Bonsai():
    """Diese Daten-Klasse enthält alle wichtigen Informationen über den Bonsaigarten."""
    __bonsaiFarmAvailability = None
    __bonsaiavailable = None
    __bonsaiquestnr = None
    __bonsaiquest = None

    def __init__(self, httpConnection: HTTPConnection):
        self._httpConn = httpConnection
        self._logBonsai = logging.getLogger('bot.Bonsai')
        self._logBonsai.setLevel(logging.DEBUG)

    def setBonsaiAvailability(self, bAvl):
        self.__bonsaiFarmAvailability = bAvl

    def isBonsaiFarmAvailable(self):
        return self.__bonsaiFarmAvailability

    def getQuestNrBonsai(self):
        return self._httpConn.getBonsaiFarmInfos()[0]

    def getQuestBonsai(self):
        return self._httpConn.getBonsaiFarmInfos()[1]

    def getBonsaiAvailable(self):
        return self._httpConn.getBonsaiFarmInfos()[2]

    def setBonsaiAvailable(self, http):
        """Liest die Anzahl der Hives aus und speichert ihn in der Klasse."""
        try:
            self.__bonsaiavailable = http.getBonsaiFarmInfos()[2]
        except:
            raise

    def setBonsaiQuestNr(self, http):
        """Liest die Anzahl der Hives aus und speichert ihn in der Klasse."""
        try:
            self.__bonsaiquestnr = http.getBonsaiFarmInfos()[0]
        except:
            raise

    def setBonsaiQuest(self, http):
        """Liest die aktuelle HoneyQuest aus und speichert ihn in der Klasse."""
        try:
            self.__bonsaiquest = http.getBonsaiFarmInfos()[1]
        except:
            raise
