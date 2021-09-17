#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 15.05.2019

@author: MrFlamez
'''

class Marketplace():
    
    def __init__(self, httpConnection):
        self.__httpConn = httpConnection
        self.__tradeableProductIDs = None
        
    def getAllTradableProducts(self):
        """
        Gibt die IDs aller handelbaren Produkte zurück.
        """
        self.updateAllTradableProducts()
        return self.__tradeableProductIDs
    
    def updateAllTradableProducts(self):
        self.__tradeableProductIDs = self.__httpConn.getAllTradeableProductsFromOverview()
    
    def getCheapestOffer(self, id):
        """
        Ermittelt das günstigste Angebot eines Produkts.
        """

        listOffers = self.getAllOffersOfProduct(id)
        
        if len(listOffers) >= 1 \
           and \
           listOffers != None:
            
            return listOffers[0][1]
        
        else: #No Offers
            return None


    def getAllOffersOfProduct(self, id):
        """
        Ermittelt alle Angebote eines Produkts.
        """
        self.updateAllTradableProducts()
        
        if self.__tradeableProductIDs != None \
           and \
           id in self.__tradeableProductIDs:

            listOffers = self.__httpConn.getOffersFromProduct(id)
        
        else: #Product is not tradeable
            listOffers = None
            
        return listOffers
    
    def findBigGapInProductOffers(self, id, npcPrice):
        """
        Ermittelt eine große Lücke (> 10 %) zwischen den Angeboten und gibt diese zurück.
        """
        
        listOffers = self.getAllOffersOfProduct(id)
        listPrices = []

        if (listOffers != None):
            
            #Alle Preise in einer Liste sammeln
            for element in listOffers:
                listPrices.append(element[1])
            
            if (npcPrice != None and id != 0): #id != 0: Coins nicht sortieren
                iList = range(0, len(listPrices))
                iList.reverse()
                for i in iList:
                    if listPrices[i] > npcPrice:
                        del listPrices[i]
            
            gaps = []
            #Zum Vergleich werden mindestens zwei Einträge benötigt.
            if (len(listPrices) >= 2):
                for i in range(0, len(listPrices)-1):
                    if (((listPrices[i+1] / 1.1) - listPrices[i]) > 0.0):
                        gaps.append([listPrices[i], listPrices[i+1]])
            
            return gaps



        