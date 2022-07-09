#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

class Honig():
    """
    Diese Daten-Klasse enthält alle wichtigen Informationen über den Honiggarten.
    """
    # Honig
    __honeyFarmAvailability = None
    __hivesavailable = None
    __honeyquestnr = None
    __honeyquest = None

    def __init__(self, httpConnection):
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
        try:
            tmpHivesAvailable = http.getHoneyFarmInfos()[2]
        except:
            raise
        else:
            self.__hivesavailable = tmpHivesAvailable

    def setHoneyQuestNr(self, http):
        """
        Liest die Anzahl der Hives aus und speichert ihn in der Klasse.
        """
        try:
            tmpHoneyQuestnr = http.getHoneyFarmInfos()[0]
        except:
            raise
        else:
            self.__honeyquestnr = tmpHoneyQuestnr

    def setHoneyQuest(self, http):
        """
        Liest die aktuelle HoneyQuest aus und speichert ihn in der Klasse.
        """
        try:
            tmpHoneyQuest = http.getHoneyFarmInfos()[1]
        except:
            raise
        else:
            self.__honeyquest = tmpHoneyQuest

    def harvest(self):
        """
        Sendet alle Bienen.
        """
        try:
            self._httpConn.harvestBienen()
        except:
            raise
        else:
            pass
    #TODO: extend and create HTTP-Requests
    def changeHivesTypeQuest(self):
        """
        Ändert die Hives auf Questanfprderungen.
        """
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
        else:
            pass