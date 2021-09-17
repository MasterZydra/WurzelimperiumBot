#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 23.01.2019

@author: MrFlamez
'''

class Product():
    
    def __init__(self, id, cat, sx, sy, name, lvl, crop, plantable, time):
        self.__id = id
        self.__category = cat
        self.__sx = sx
        self.__sy = sy
        self.__name = name
        self.__level = lvl
        self.__crop = crop
        self.__isPlantable = plantable
        self.__timeUntilHarvest = time
        self.__priceNPC = None

        
    def getID(self):
        return self.__id
    
    def getName(self):
        return self.__name
    
    def getSX(self):
        return self.__sx

    def getSY(self):
        return self.__sy
    
    def getPriceNPC(self):
        return self.__priceNPC
    
    def isProductPlantable(self):
        return self.__isPlantable
        
    def setPriceNPC(self, price):
        self.__priceNPC = price
        
    def printAll(self):
        print 'ID: ', str(self.__id).ljust(5), \
              'CAT: ', str(self.__category).ljust(8), ' ', \
              'Name: ', str(self.__name).ljust(50), ' ', \
              'NPC: ', str(self.__priceNPC).ljust(10), ' ', \
              'SX: ', str(self.__sx).ljust(4), ' ', \
              'SY: ', str(self.__sy).ljust(4)



"""
Kategorie   category ['z', '', 'd', 'v', 'w', 'u', 'wd', 'honey', None, 'h']

#Nur in 344, 273, 274, 330, 333, 345, 324, 363, 282: 'speedup_cooldown', 'speedup_reduction'
"""


