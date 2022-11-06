#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 21.03.2017

@author: Gosha_iv
"""

from src.HTTPCommunication import HTTPConnection
from src.Produktdaten import ProductData

class Wimps:
    def __init__(self, httpConnection: HTTPConnection):
        self.__httpConn = httpConnection

    def getWimpsData(self, garden):
        return self.__httpConn.getWimpsData(garden._id)

    def sellWimpProducts(self, wimp_id):
        return self.__httpConn.sellWimpProducts(wimp_id)

    def declineWimp(self, wimp_id):
        return self.__httpConn.declineWimp(wimp_id)
    
    def productsToString(self, products, productData: ProductData):
        result = "Price: " + str(products[0]) + " wT"
        for product, amount in products[1].items():
            result += "\n" + str(amount) + "x " + productData.getProductByID(product).getName()
        return result