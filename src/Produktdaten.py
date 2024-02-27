#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 23.05.2019

@author: MrFlamez
'''

import json
from src.core.HTTPCommunication import HTTPConnection
from src.Produkt import Product

CATEGORY_DECORATION       = 'd'
CATEGORY_HERBS            = 'h'
CATEGORY_HONEY            = 'honey'
CATEGORY_WATER_PLANTS     = 'w'
CATEGORY_VEGETABLES       = 'v'
CATEGORY_WATER_DECORATION = 'wd'
CATEGORY_COINS            = ''
CATEGORY_ADORNMENTS       = 'z'
CATEGORY_OTHER            = 'u'

class ProductData():
    def __init__(self, httpConnection: HTTPConnection):
        self.__httpConn = httpConnection
        self.__products = []

    def __setAllPricesOfNPC(self):
        dNPC = self.__httpConn.getNPCPrices()
        for product in self.__products:
            productname = product.getName()
            if productname in dNPC:
                product.setPriceNPC(dNPC[productname])

    def getProductByID(self, id):
        for product in self.__products:
            if int(id) == int(product.getID()):
                return product
        return None

    def getProductByName(self, name : str):
        name = name.lower()
        for product in self.__products:
            if name == product.getName().lower():
                return product
        return None

    def getListOfAllProductIDs(self):
        return [product.getID() for product in self.__products]

    def getListOfSingleFieldVegetables(self):
        return [product.getName() for product in self.__products if product.getSX() == 1 and product.getSY() == 1 and product.isVegetable() and product.isPlantable()]

    def initAllProducts(self):
        products = self.__httpConn.getAllProductInformations()
        dictProducts = json.loads(products)
        for key in sorted(dictProducts.keys()):
            if key == '999':
                continue
            sx = dictProducts[key].get('sx', 0)
            sy = dictProducts[key].get('sy', 0)
            name = dictProducts[key]['name'].replace('&nbsp;', ' ')
            self.__products.append(Product(id=int(key), cat=dictProducts[key]['category'], sx=sx, sy=sy, name=name.encode('utf-8'), lvl=dictProducts[key]['level'], crop=dictProducts[key]['crop'], plantable=dictProducts[key]['plantable'], time=dictProducts[key]['time'], edge=dictProducts[key]['edge']))
        self.__setAllPricesOfNPC()

    def printAll(self):
        sortedProducts = sorted(self.__products, key=lambda x: x.getName().lower())
        for product in sortedProducts:
            product.printAll()

    def printAllVegetables(self):
        sortedProducts = sorted(self.__products, key=lambda x: x.getName().lower())
        for product in sortedProducts:
            if product.isVegetable():
                product.printAll()

    def printAllWaterPlants(self):
        sortedProducts = sorted(self.__products, key=lambda x: x.getName().lower())
        for product in sortedProducts:
            if product.isWaterPlant():
                product.printAll()
