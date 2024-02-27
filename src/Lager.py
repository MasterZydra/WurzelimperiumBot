#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict

class Storage():
    def __init__(self, httpConnection):
        self.__httpConn = httpConnection
        self.__products = defaultdict(int)

    def __resetNumbersInStock(self):
        self.__products.clear()

    def initProductList(self, productList):
        self.__products.update({str(productID): 0 for productID in productList})

    def updateNumberInStock(self):
        try:
            inventory = self.__httpConn.getInventory()
            self.__products.update({str(productID): quantity for productID, quantity in inventory.items()})
        except Exception as e:
            print(f"Error updating stock: {e}")

    def getStockByProductID(self, productID):
        return self.__products[str(productID)]

    def getKeys(self):
        return list(self.__products.keys())

    def getOrderedStockList(self):
        sortedStock = {k: v for k, v in sorted(self.__products.items(), key=lambda item: item[1]) if v != 0}
        return sortedStock

    def getLowestStockEntry(self):
        orderedStock = self.getOrderedStockList()
        if orderedStock:
            return next(iter(orderedStock))
        return None

