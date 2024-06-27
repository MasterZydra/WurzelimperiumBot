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
    
    accountLogin = None
    __userName = None
    __userID = None
    numberOfGardens = None
    __userData = None
    __honeyFarmAvailability = None
    __aquaGardenAvailability = None
    __bonsaiFarmAvailability = None
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
    
    def is_premium_active(self) -> int:
        """returns state of premium account
        Returns:
            int: 0 = no premium, 1 = premium active
        """
        return int(self.__userData['citymap']['premium'])
    
    def is_guild_member(self) -> bool:
        """Returns false if no guild_tag is set, otherwise true"""
        if self.__userData['g_tag'] == "":
            return False
        return True

    def setUserNameFromServer(self, http):
        """
        Liest den Spielernamen vom Server und speichert ihn in der Klasse.
        """
        try:
            self.__userName = http.getInfoFromStats("Username")
        except:
            raise
    
    def setUserDataFromServer(self, http):
        """
        Liest den Spielerdaten vom Server und speichert sie in der Klasse.
        """
        try:
            self.__userData = http.readUserDataFromServer()
        except:
            print('Status der E-Mail Adresse konnte nicht ermittelt werden.')

    def setUserID(self, userID):
        self.__userID = userID
        
    def setConfirmedEMailAdressFromServer(self, http):
        """
        Liest vom Server, ob die E-Mail Adresse bestätigt ist und speichert den Status in der KLasse.
        """
        try:
            self.__eMailAdressConfirmed = http.checkIfEMailAdressIsConfirmed()
        except:
            pass
