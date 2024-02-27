#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from src.core.HTTPCommunication import HTTPConnection

class Park:

    def __init__(self, httpConnection: HTTPConnection):
        self._httpConn = httpConnection
        self._logPark = logging.getLogger('bot.Park')
        self._logPark.setLevel(logging.DEBUG)
        self.__setParkData(self._httpConn.initPark())

    def __setParkData(self, jContent):
        """Set the relevant park data from the JSON content."""
        self._jContentData = jContent['data']
        self._cashpoint = jContent["data"]["data"]["cashpoint"]
        self._logPark.debug("Park data set.")

    def collectCashFromCashpoint(self):
        """Collect rewards from the cashpoint if there are any."""
        cashpoint_money = self._jContentData['data']["cashpoint"]["money"]
        if cashpoint_money <= 0:
            self._logPark.error("The Cashpoint is empty.")
            return
        jContent = self._httpConn.collectCashPointFromPark()
        self._logPark.info(f"Collected: {self._cashpoint['points']} points, {self._cashpoint['money']} wT, {self._cashpoint['parkpoints']} parkpoints")
        self.__setParkData(jContent)

    def __getExpiredDekoFromPark(self, parkID=1):
        """Get all expired items."""
        items = self._jContentData["data"]["park"][str(parkID)]["items"]
        renewableItems = {key: value for key, value in items.items() if 'parent' not in value and value["remain"] < 0}
        self._logPark.info("Renewable items: {}".format(len(renewableItems)))
        return renewableItems

    def renewAllItemsInPark(self):
        """Renew all expired items."""
        renewableItems = self.__getExpiredDekoFromPark()
        for itemID in renewableItems:
            jContent = self._httpConn.renewItemInPark(itemID)
            self.__setParkData(jContent)
        self._logPark.info(f"Renewed {len(renewableItems)} items.")