#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 21.03.2017
@author: MrFlamez
'''
from collections import namedtuple
import i18n
import html

# Laden von Übersetzungsdateien
i18n.load_path.append('lang')

# Definition eines benannten Tupels für den Login
Login = namedtuple('Login', 'server user password language')


class Spieler:
    """
    Diese Daten-Klasse enthält alle wichtigen Informationen über den Spieler.
    """

    #BG-Тази класа данни съдържа цялата важна информация за играча.

    def __init__(self) -> None:
        self.accountLogin = None
        self.__userName = None
        self.__userID = None
        self.numberOfGardens = None
        self.__userData = None
        self.__honeyFarmAvailability = None
        self.__aquaGardenAvailability = None
        self.__bonsaiFarmAvailability = None
        self.__cityParkAvailability = None
        self.__eMailAdressConfirmed = None

    def setHoneyFarmAvailability(self, bAvl: bool) -> None:
        self.__honeyFarmAvailability = bAvl

    def isHoneyFarmAvailable(self) -> bool:
        return self.__honeyFarmAvailability

    def setBonsaiFarmAvailability(self, bAvl: bool) -> None:
        self.__bonsaiFarmAvailability = bAvl

    def isBonsaiFarmAvailable(self) -> bool:
        return self.__bonsaiFarmAvailability

    def setAquaGardenAvailability(self, bAvl: bool) -> None:
        self.__aquaGardenAvailability = bAvl

    def isAquaGardenAvailable(self) -> bool:
        return self.__aquaGardenAvailability

    def setCityParkAvailability(self, bAvl: bool) -> None:
        self.__cityParkAvailability = bAvl

    def isCityParkAvailable(self) -> bool:
        return self.__cityParkAvailability

    def isEMailAdressConfirmed(self) -> bool:
        return self.__eMailAdressConfirmed

    def getUserName(self) -> str:
        return self.__userName

    def getLevelNr(self) -> int:
        return self.__userData['levelnr']

    def getLevelName(self) -> str:
        return html.unescape(self.__userData['level'])

    def getBar(self) -> str:
        return self.__userData['bar_unformat']

    def getPoints(self) -> int:
        return self.__userData['points']

    def getTime(self) -> str:
        return self.__userData['time']

    def getCoins(self) -> int:
        return self.__userData['coins']

    def getBarFormated(self) -> str:
        return self.__userData['bar']

    def setUserNameFromServer(self, http) -> None:
        """
        Liest den Spielernamen vom Server und speichert ihn in der Klasse.
        """
        # BG-Прочита името на играча от сървъра и го съхранява в класа.
        try:
            self.__userName = http.getInfoFromStats("Username")
        except Exception as e:
            raise e

    def setUserDataFromServer(self, http) -> None:
        """
        Liest den Spielerdaten vom Server und speichert sie in der Klasse.
        """
        # BG-Прочита данните за играча от сървъра и ги съхранява в класа.
        try:
            self.__userData = http.readUserDataFromServer()
        except Exception as e:
            print('Status der E-Mail Adresse konnte nicht ermittelt werden.')
            # BG- print('Състоянието на имейл адреса не можа да бъде определено.')

    def setUserID(self, userID: int) -> None:
        self.__userID = userID

    def setConfirmedEMailAdressFromServer(self, http) -> None:
        """
        Liest vom Server, ob die E-Mail Adresse bestätigt ist und speichert den Status in der Klasse.
        """
        # BG-Прочита от сървъра дали имейл адресът е потвърден и съхранява статуса в класа.
        try:
            self.__eMailAdressConfirmed = http.checkIfEMailAdressIsConfirmed()
        except Exception:
            pass
