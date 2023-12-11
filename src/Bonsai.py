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
    
    def getBonsaiSlotInfo(self):
        return self._httpConn.getBonsaiFarmInfos()[4]

    def setBonsaiAvailable(self, http: HTTPConnection):
        """Liest die Anzahl der Hives aus und speichert ihn in der Klasse."""
        try:
            self.__bonsaiavailable = http.getBonsaiFarmInfos()[2]
        except:
            raise

    def setBonsaiQuestNr(self, http: HTTPConnection):
        """Liest die Anzahl der Hives aus und speichert ihn in der Klasse."""
        try:
            self.__bonsaiquestnr = http.getBonsaiFarmInfos()[0]
        except:
            raise

    def setBonsaiQuest(self, http: HTTPConnection):
        """Liest die aktuelle HoneyQuest aus und speichert ihn in der Klasse."""
        try:
            self.__bonsaiquest = http.getBonsaiFarmInfos()[1]
        except:
            raise

    

    def doCutBonsai(self, http: HTTPConnection):
        #TODO Item automatisch nach kaufen, Bonsai in den Garten setzen wenn lvl 3 erreicht
        """
        Probiert bei allen Bäumen die Äste zu schneiden
        """
        sissor = None
        sissor_loads = 0
        for key, value in http.getBonsaiFarmInfos()[3]['data']['items'].items():
            if value['item'] == "21":
                sissor = key
                sissor_loads = value['loads']
                print(f"Key: {key}; value: {value}")
        if sissor_loads < 50:
            self.buyScissors(http)
        if sissor is None:
            print("No scissors found...")
            pass
        
        slotinfos = http.getBonsaiSlotInfos()
        for key in slotinfos.keys():
            for branch in slotinfos[key][2]:
                http.doCutBonsaiBranch(key, branch, sissor)

    def buyScissors(self, http: HTTPConnection):
        http.buyScissors()
