#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 21.03.2017

@author: Gosha_iv
"""

class Wimps:


    def __init__(self, httpConnection):
        self.__httpConn = httpConnection
        # self.__wimpData = {}

    def getWimpsData(self, garden):
        wimpsData = self.__httpConn.getWimpsData(garden._id)
        return wimpsData

