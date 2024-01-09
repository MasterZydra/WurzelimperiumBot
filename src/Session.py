#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 21.01.2017

@author: MrFlamez
'''

import time, logging, i18n

i18n.load_path.append('lang')


class Session(object):
    """
    Die Session Klasse ist das Python-Pendant einer PHP-Session und dieser daher nachempfunden.
    """
    #BG-Този клас е Python еквивалент на PHP сесия и е проектиран по подобен начин.
    #Gültigkeitsdauer der Session (2 h -> 7200 s)
    #BG-Продължителност на валидност на сесията (2 h -> 7200 s)
    __lifetime         = 7200
    __lifetime_reserve =  300

    #Eine Reservezeit dient dazu, kurz vor Ende der Session rechtzeitig alle Aktionen
    #abschließen zu können
    #BG-Резервно време е необходимо, за да могат всички действия да бъдат завършени навреме преди края на сесията.
    def __init__(self):
        """
        Initialisierung aller Attribute mit einem Standardwert.
        """
        #BG-Инициализация на всички атрибути със стандартен/и стойност/и.
        self.__logSession = logging.getLogger('bot.Session')
        self.__sessionID = None
        self.__serverURL = None
        self.__server = None
        self.__startTime = None
        self.__endTime = None

    def __isSessionTimeElapsed(self):
        """Prüft, ob die offene Session abgelaufen ist."""
        #BG-Проверява дали отворената сесия е изтекла.
        return time.time() > self.__endTime

    def isSessionValid(self): #TODO: Prüfen wie die Methode sinnvoll eingesetzt werden kann
        """Prüft anhand verschiedener Kriterien, ob die aktuelle Session gültig ist."""
        #BG-Проверява валидността на текущата сесия по различни критерии.
        bReturn = True
        if (self.__sessionID == None): bReturn = False
        if (self.__isSessionTimeElapsed()): bReturn = False
        return bReturn

    def openSession(self, sessionID, server, serverURL):
        """
        Anlegen einer neuen Session mit allen notwendigen Daten.
        """
        #BG-Създаване на нова сесия с всички необходими данни.
        self.__sessionID = sessionID
        self.__server = server
        self.__serverURL = serverURL

        self.__startTime = time.time()
        self.__endTime = self.__startTime + (self.__lifetime - self.__lifetime_reserve)

        sID = str(self.__sessionID)
        self.__logSession.info(f'Session (ID: {sID}) geöffnet')

    def closeSession(self, wunr, server):
        """
        Zurücksetzen aller Informationen. Gleichbedeutend mit einem Schließen der Session.
        """
        #BG-Нулиране на цялата информация. Еквивалентно на затваряне на сесията.
        sID = str(self.__sessionID)
        self.__sessionID = None
        self.__server = None
        self.__startTime = None
        self.__endTime = None
        self.__logSession.info(f'Session (ID: {sID}) geschlossen')

    def getRemainingTime(self):
        """Gibt die verbleibende Zeit zurück, bis die Session abläuft."""
        #BG-Връща оставащото време до изтичане на сесията.
        return self.__endTime - time.time()

    def getSessionID(self):
        """Gibt die Session-ID zurück."""
        #BG-Връща ID на сесията.
        return self.__sessionID

    def getServer(self):
        """Gibt die Servernummer zurück."""
        #BG-Връща номера на сървъра.
        return self.__server

    def getServerURL(self):
        """Returns the server URL."""
        #BG-Връща URL адреса на сървъра.
        return self.__serverURL
