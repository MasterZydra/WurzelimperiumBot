#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 21.03.2017

@author: Gosha_iv
"""

class Wimps:

    def __init__(self, httpConnection):
        self.__httpConn = httpConnection


    def getWimpsData(self, garden):
        wimpsData = self.__httpConn.getWimpsData(garden._id)
        return wimpsData

    def sellWimpProducts(self, wimp_id):
        result = self.__httpConn.sellWimpProducts(wimp_id)
        return result

    def declineWimp(self, wimp_id):
        result = self.__httpConn.declineWimp(wimp_id)