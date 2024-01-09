#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.HTTPCommunication import HTTPConnection

class Storage():
    def __init__(self, httpConnection: HTTPConnection):
        self.__httpConn = httpConnection
        self.__products = {}

    def __resetNumbersInStock(self):
        for productID in self.__products.keys():
            self.__products[productID] = 0

    def initProductList(self, productList):
        for productID in productList:
            self.__products[str(productID)] = 0

    def updateNumberInStock(self):
        """Aktualisiert den Lagerbestand für alle Produkte."""
        #BG-Актуализира наличните количества за всички продукти.
        self.__resetNumbersInStock()

        inventory = self.__httpConn.getInventory()
        for i in inventory:
            self.__products[i] = inventory[i]

    def getStockByProductID(self, productID):
        return self.__products[str(productID)]

    def getKeys(self):
        return self.__products.keys()

    def getOrderedStockList(self):
        sortedStock = dict(sorted(self.__products.items(), key=lambda item: item[1]))
        filteredStock = dict()
        for productID in sortedStock:
            if sortedStock[str(productID)] == 0: continue
            filteredStock[str(productID)] = sortedStock[str(productID)]
        return filteredStock

    def getLowestStockEntry(self):
        for productID in self.getOrderedStockList().keys():
            return productID
        return -1
