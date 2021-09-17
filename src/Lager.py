#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Storage():
    
    def __init__(self, httpConnection):
        self.__httpConn = httpConnection
        self.__products = {}


    def __resetNumbersInStock(self):
        for productID in self.__products.keys():
            self.__products[productID] = 0


    def initProductList(self, productList):
        
        for productID in productList:
            self.__products[str(productID)] = 0
        
    
    def updateNumberInStock(self):
        """
        Führt ein Update des Lagerbestands für alle Produkte durch.
        """
        
        self.__resetNumbersInStock()
            
        inventory = self.__httpConn.getInventory()
        
        for i in inventory:
            self.__products[i] = inventory[i]



