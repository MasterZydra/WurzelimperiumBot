#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 21.03.2017

@author: Gosha_iv
"""

from src.core.HTTPCommunication import HTTPConnection
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

    def products_to_string(self, products, productData: ProductData):
        price = products[0]
        product_details = products[1]

        result = f"Price: {price} wT"
        for product_id, amount in product_details.items():
            product_name = productData.getProductByID(product_id).getName()
            result += f"\n{amount}x {product_name}"

        return result 
