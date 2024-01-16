#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from src.core.HTTPCommunication import HTTPConnection

class Park():

    def __init__(self, httpConnection: HTTPConnection):
        self._httpConn = httpConnection
        self._logPark = logging.getLogger('bot.Park')
        self._logPark.setLevel(logging.DEBUG)
        self.__setParkData(self._httpConn.initPark())

    def __setParkData(self, jContent):
        """set the relevant park data from the JSON content"""
        self._jContentData = jContent['data']
        self._cashpoint = jContent["data"]["data"]["cashpoint"]

    def collectCashFromCashpoint(self):
        """collect rewards from cashpoint if there are any"""
        if not self._jContentData['data']["cashpoint"]["money"] > 0:
            self._logPark.error("The Cashpoint is empty.")
        else:
            jContent = self._httpConn.collectCashPointFromPark()
            self._logPark.info("Collected: {points} points, {money} wT, {parkpoints} parkpoints".format(points = self._cashpoint["points"], money = self._cashpoint["money"], parkpoints=self._cashpoint["parkpoints"]))
            self.__setParkData(jContent)

    def __getExpiredDekoFromPark(self, parkID=1):
        """get all expired items"""
        items = self._jContentData["data"]["park"][str(parkID)]["items"]
        renewableItems = {}
        for key, value in items.items():
            if 'parent' in value: 
                continue
            if value["remain"] < 0:
                renewableItems.update({key:value})
        self._logPark.info("renewable items: {}".format(len(renewableItems)))            
        return renewableItems
    
    def renewAllItemsInPark(self):
        """renew all expired items"""
        renewableItems = self.__getExpiredDekoFromPark()
        for itemID in renewableItems.keys():
            jContent = self._httpConn.renewItemInPark(itemID)
            self.__setParkData(jContent)
        self._logPark.info("Renewed {} Items.".format(len(renewableItems)))
            
