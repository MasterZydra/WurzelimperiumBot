#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from src.core.HTTPCommunication import HTTPConnection

class Honig():
    """
    Diese Daten-Klasse enthält alle wichtigen Informationen über den Honiggarten.
    """
    #BG- Тази класа данни съдържа цялата важна информация за пчелната градина.

    # Honig
    #BG- Мед
    __honeyFarmAvailability = None
    __hivesavailable = None
    __honeyquestnr = None
    __honeyquest = None

    def __init__(self, httpConnection: HTTPConnection):
        self._httpConn = httpConnection
        self._logHonig = logging.getLogger('bot.Honig')
        self._logHonig.setLevel(logging.DEBUG)

    def setHoneyFarmAvailability(self, bAvl):
        self.__honeyFarmAvailability = bAvl

    def isHoneyFarmAvailable(self):
        return self.__honeyFarmAvailability

    def getQuestNrHoney(self):
        return self._httpConn.getHoneyFarmInfos()[0]

    def getQuestHoney(self):
        return self._httpConn.getHoneyFarmInfos()[1]

    def getHivesAvailable(self):
        return self._httpConn.getHoneyFarmInfos()[2]

    def getHiveType(self):
        return self._httpConn.getHoneyFarmInfos()[3]

    def setHivesAvailable(self, http):
        """
        Liest die Anzahl der Hives aus und speichert ihn in der Klasse.
        """
        #BG- Четене на броя на кошерите и съхраняването му в класа.
        try:
            self.__hivesavailable = http.getHoneyFarmInfos()[2]
        except:
            raise

    def setHoneyQuestNr(self, http):
        """
        Liest die Anzahl der Hives aus und speichert ihn in der Klasse.
        """
        #BG- Четене на броя на кошерите и съхраняването му в класа.
        try:
            self.__honeyquestnr = http.getHoneyFarmInfos()[0]
        except:
            raise

    def setHoneyQuest(self, http):
        """
        Liest die aktuelle HoneyQuest aus und speichert ihn in der Klasse.
        """
        #BG- Четене на текущата HoneyQuest и съхраняването ѝ в класа.
        try:
            self.__honeyquest = http.getHoneyFarmInfos()[1]
        except:
            raise

    def harvest(self):
        """Sendet alle Bienen."""
        #BG- Изпраща всички пчели.
        try:
            self._httpConn.harvestBienen()
        except:
            raise

    #TODO: extend and create HTTP-Requests
    def changeHivesTypeQuest(self):
        """Ändert die Hives auf Questanforderungen."""
        #BG- Променя кошерите според изискванията на куеста.
        quest = self.__honeyquest
        for i in quest:
            if quest[i]['missing'] != 0:
                change = quest[i]['pid']
                break
            else:
                change = 315

        Questanforderung = change
        try:
            self._httpConn.changeHiveBienen(Questanforderung)
        except:
            raise
