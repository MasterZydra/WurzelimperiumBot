#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 23.05.2019

@author: MrFlamez
'''

import json
from src.HTTPCommunication import HTTPConnection
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
        """Ermittelt alle möglichen NPC Preise und setzt diese in den Produkten."""
        dNPC = self.__httpConn.getNPCPrices()
        dNPCKeys = dNPC.keys()
        
        product: Product
        for product in self.__products:
            productname = product.getName()
            if productname in dNPCKeys:
                product.setPriceNPC(dNPC[productname])
                
        #Coin manuell setzen, dieser ist in der Tabelle der Hilfe nicht enthalten
        coins = self.getProductByName('Coins')
        coins.setPriceNPC((300.0))

    def getProductByID(self, id):
        product: Product
        for product in self.__products:
            if int(id) == int(product.getID()): return product
        return None

    def getProductByName(self, name : str):
        product: Product
        for product in self.__products:
            if (name.lower() == product.getName().lower()): return product
        return None

    def getListOfAllProductIDs(self):
        productIDList = []
        product: Product
        for product in self.__products:
            id = product.getID()
            productIDList.append(id)
            
        return productIDList

    def getListOfSingleFieldPlants(self):
        singleFieldPlants = []
        product: Product
        for product in self.__products:
            if product.getSX() != 1 or product.getSY() != 1 \
            or not product.isVegetable() or not product.isPlantable():
                continue
        
            singleFieldPlants.append(product.getName())

        return singleFieldPlants

    def initAllProducts(self):
        """Initialisiert alle Produkte."""
        products = self.__httpConn.getAllProductInformations()
        jProducts = json.loads(products)
        dictProducts = dict(jProducts)
        keys = dictProducts.keys()
        keys = sorted(keys)
        # Nicht genutzte Attribute: img, imgPhase, fileext, clear, edge, pieces, speedup_cooldown in Kategorie z
        for key in keys:
            # 999 ist nur ein Testeintrag und wird nicht benötigt.
            if key == '999':
                continue
                
            # Skip products without field sizes (e.g. honey)
            if not 'sx' in dictProducts[key]:
                continue

            name = dictProducts[key]['name'].replace('&nbsp;', ' ')
            self.__products.append(Product(id        = int(key), \
                                           cat       = dictProducts[key]['category'], \
                                           sx        = dictProducts[key]['sx'], \
                                           sy        = dictProducts[key]['sy'], \
                                           name      = name.encode('utf-8'), \
                                           lvl       = dictProducts[key]['level'], \
                                           crop      = dictProducts[key]['crop'], \
                                           plantable = dictProducts[key]['plantable'], \
                                           time      = dictProducts[key]['time']))
                
        self.__setAllPricesOfNPC()

    def printAll(self):
        sortedProducts = sorted(self.__products, key=lambda x:x.getName().lower())
        product: Product
        for product in sortedProducts:
            product.printAll()

    def printAllVegetables(self):
        sortedProducts = sorted(self.__products, key=lambda x:x.getName().lower())
        product: Product
        for product in sortedProducts:
            if not product.isVegetable():
                continue
            product.printAll()

    def printAllWaterPlants(self):
        sortedProducts = sorted(self.__products, key=lambda x:x.getName().lower())
        product: Product
        for product in sortedProducts:
            if not product.isWaterPlant():
                continue
            product.printAll()