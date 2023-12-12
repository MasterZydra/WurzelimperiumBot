#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from src.HTTPCommunication import HTTPConnection

class Park():

    def __init__(self, httpConnection: HTTPConnection):
        self._httpConn = httpConnection
        self._logPark = logging.getLogger('bot.Park')
        self._logPark.setLevel(logging.DEBUG)
        self.__setParkData(self._httpConn.initPark())

    def __setParkData(self, jContent):
        self._jContentData = jContent['data']
        self._cashpoint = jContent["data"]["data"]["cashpoint"]

    def collectCashFromCashpoint(self):
        if not self._jContentData['data']["cashpoint"]["money"] > 0:
            self._logPark.error("Es konnte kein Geld oder Punkte abgeholt werden.")
        jContent = self._httpConn.collectCashPointFromPark()
        self._logPark.info("Es wurden {points} Punkte, {money} Wurzeltaler, {parkpoints} Gartenpunkte abgeholt".format(points = self._cashpoint["points"], money = self._cashpoint["money"], parkpoints=self._cashpoint["parkpoints"]))
        self.__setParkData(jContent)

    def __getRenewableDekoFromPark(self, parkID=1):
        items = self._jContentData["data"]["park"][str(parkID)]["items"]
        renewableItems = {}
        for key, value in items.items():
            if 'parent' in value: 
                continue
            if value["remain"] < 0:
                renewableItems.update({key:value})
        self._logPark.info("Es können {} Items erneuert werden.".format(len(renewableItems)))            
        return renewableItems
    
    def renewAllItemsInPark(self):
        renewableItems = self.__getRenewableDekoFromPark()
        for itemID in renewableItems.keys():
            self._logPark.info(f"Erneuere tile: {itemID}")
            # jContent = self._httpConn.renewItemInPark(itemID)
            # self.setParkData(jContent)
        self._logPark.info("Es wurden {} Items erneuert.".format(len(renewableItems)))
            
