#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 21.03.2017
@author: MrFlamez
'''
from collections import namedtuple
import i18n, html

i18n.load_path.append('lang')

Login = namedtuple('Login', 'server user password language')

class Spieler():

    """
    Diese Daten-Klasse enthält alle wichtigen Informationen über den Spieler.
    """
    #BG-Тази класа данни съдържа цялата важна информация за играча.
    accountLogin = None
    __userName = None
    __userID = None
    numberOfGardens = None
    __userData = None
    __honeyFarmAvailability = None
    __aquaGardenAvailability = None
    __bonsaiFarmAvailability = None
    __cityParkAvailability = None
    __eMailAdressConfirmed = None

    def __init__(self):
        pass

    def setHoneyFarmAvailability(self, bAvl):
        self.__honeyFarmAvailability = bAvl

    def isHoneyFarmAvailable(self):
        return self.__honeyFarmAvailability

    def setBonsaiFarmAvailability(self, bAvl):
        self.__bonsaiFarmAvailability = bAvl

    def isBonsaiFarmAvailable(self):
        return self.__bonsaiFarmAvailability

    def setAquaGardenAvailability(self, bAvl):
        self.__aquaGardenAvailability = bAvl

    def isAquaGardenAvailable(self):
        return self.__aquaGardenAvailability

    def setCityParkAvailability(self, bAvl):
        self.__cityParkAvailability = bAvl

    def isCityParkAvailable(self):
        return self.__cityParkAvailability

    def isEMailAdressConfirmed(self):
        return self.__eMailAdressConfirmed

    def getUserName(self):
        return self.__userName

    def getLevelNr(self):
        return self.__userData['levelnr']

    def getLevelName(self):
        return html.unescape(self.__userData['level'])

    def getBar(self):
        return self.__userData['bar_unformat']

    def getPoints(self):
        return self.__userData['points']

    def getTime(self):
        return self.__userData['time']

    def getCoins(self):
        return self.__userData['coins']

    def getBarFormated(self):
        return self.__userData['bar']

    def setUserNameFromServer(self, http):
        """
        Liest den Spielernamen vom Server und speichert ihn in der Klasse.
        """
        #BG-Прочита името на играча от сървъра и го съхранява в класа.
        try:
            self.__userName = http.getInfoFromStats("Username")
        except:
            raise

    def setUserDataFromServer(self, http):
        """
        Liest den Spielerdaten vom Server und speichert sie in der Klasse.
        """
        #BG-Прочита данните за играча от сървъра и ги съхранява в класа.
        try:
            self.__userData = http.readUserDataFromServer()
        except:
            print('Status der E-Mail Adresse konnte nicht ermittelt werden.')
            #BG- print('Състоянието на имейл адреса не можа да бъде определено.')
    def setUserID(self, userID):
        self.__userID = userID

    def setConfirmedEMailAdressFromServer(self, http):
        """
        Liest vom Server, ob die E-Mail Adresse bestätigt ist und speichert den Status in der KLasse.
        """
        #BG-Прочита от сървъра дали имейл адресът е потвърден и съхранява статуса в класа.
        try:
            self.__eMailAdressConfirmed = http.checkIfEMailAdressIsConfirmed()
        except:
            pass
