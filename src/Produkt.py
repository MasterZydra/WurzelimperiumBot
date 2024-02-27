#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 23.01.2019

@author: MrFlamez
'''

import datetime

class Product():
    def __init__(self, id, cat, sx, sy, name, lvl, crop, plantable, time, edge):
        self.__id = id
        self.__category = cat
        self.__sx = sx
        self.__sy = sy
        self.__name = name.decode('UTF-8')
        self.__level = lvl
        self.__crop = crop
        self.__isPlantable = plantable
        self.__timeUntilHarvest = time
        self.__edge = edge
        self.__priceNPC = None

    def getID(self):
        return self.__id

    def getCategory(self):
        return self.__category

    def getCrop(self):
        return self.__crop

    def getName(self):
        return self.__name

    def getSX(self):
        return self.__sx

    def getSY(self):
        return self.__sy

    def getEdge(self):
        return self.__edge

    def getPriceNPC(self):
        return self.__priceNPC

    def isPlantable(self):
        return self.__isPlantable

    def isVegetable(self):
        return self.__category == "v" and self.__priceNPC is not None

    def isWaterPlant(self):
        return self.__category == "w"

    def isDecoration(self):
        return self.__category == "d"

    def setPriceNPC(self, price):
        self.__priceNPC = price

    def printAll(self):
        print('ID:', str(self.__id).rjust(3), 
              'CAT:', str(self.__category).ljust(5), 
              'Name:', str(self.__name).ljust(35), 
              'Plantable:', str(self.__isPlantable).ljust(5), 
              'NPC:', str(self.__priceNPC).rjust(6) if self.__priceNPC is not None else "", 
              'Time:', str(datetime.timedelta(seconds=self.__timeUntilHarvest)).rjust(8), 
              'SX:', str(self.__sx) if self.__sx is not None else "", 
              'SY:', str(self.__sy) if self.__sy is not None else "")

"""
Kategorie   category ['z', '', 'd', 'v', 'w', 'u', 'wd', 'honey', None, 'h']
d = Dekoration
v = vegetables??

#Nur in 344, 273, 274, 330, 333, 345, 324, 363, 282: 'speedup_cooldown', 'speedup_reduction'
"""
