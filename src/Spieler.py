#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 21.03.2017
@author: MrFlamez
'''
from collections import namedtuple


Login = namedtuple('Login', 'server user password')

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
    __eMailAdressConfirmed = None

    def __init__(self):
        pass

    def setHoneyFarmAvailability(self, bAvl):
        self.__honeyFarmAvailability = bAvl

    def isHoneyFarmAvailable(self):
        return self.__honeyFarmAvailability

    def setAquaGardenAvailability(self, bAvl):
        self.__aquaGardenAvailability = bAvl

    def isAquaGardenAvailable(self):
        return self.__aquaGardenAvailability
    
    def isEMailAdressConfirmed(self):
        return self.__eMailAdressConfirmed
    
    def getUserName(self):
        return self.userName
    
    def getLevelNr(self):
        return self.__userData['levelnr']
    
    def setUserNameFromServer(self, http):
        """
        Liest den Spielernamen vom Server und speichert ihn in der Klasse.
        """
        try:
            tmpUserName = http.getUserName()
        except:
            raise
        else:
            self.__userName = tmpUserName
    
    def setUserDataFromServer(self, http):
        """
        Liest den Spielerdaten vom Server und speichert sie in der Klasse.
        """
        try:
            tmpUserData = http.readUserDataFromServer()
        except:
            print 'Status der E-Mail Adresse konnte nicht ermittelt werden.'
        else:
            self.__userData = tmpUserData
            
    def setUserID(self, userID):
        self.__userID = userID
        
    def setConfirmedEMailAdressFromServer(self, http):
        """
        Liest vom Server, ob die E-Mail Adresse bestätigt ist und speichert den Status in der KLasse.
        """
        try:
            tmpEMailConf = http.checkIfEMailAdressIsConfirmed()
        except:
            pass
        else:
            self.__eMailAdressConfirmed = tmpEMailConf
            

