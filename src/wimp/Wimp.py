#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 21.03.2017

@author: Gosha_iv
"""

from src.wimp.Http import Http
from src.Produktdaten import ProductData

class Wimp:
    def __init__(self):
        self.__http = Http()

    def get_wimps_data(self, garden):
        return self.__http.get_wimps_data(garden._id)

    def sell(self, wimp_id):
        return self.__http.sell_to_wimp(wimp_id)

    def decline(self, wimp_id):
        return self.__http.decline_wimp(wimp_id)

    def products_to_string(self, products, productData: ProductData):
        result = "Price: " + str(products[0]) + " wT"
        for product, amount in products[1].items():
            result += "\n" + str(amount) + "x " + productData.getProductByID(product).get_name()
        return result 
