#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 15.05.2019

@author: MrFlamez
'''

from src.marketplace.Http import Http

class Marketplace:
    def __init__(self):
        self.__http = Http()
        self.__tradeable_product_ids = None

    def get_all_tradable_products(self):
        """Returns the IDs of all tradable products"""
        if not self.update_tradable_products():
            return None
        return self.__tradeable_product_ids

    def update_tradable_products(self) -> bool:
        self.__tradeable_product_ids = self.__http.get_tradeable_products_from_overview()
        return self.__tradeable_product_ids is not None

    def get_cheapest_offer(self, id):
        """Determine the cheapest offer for a product"""
        offers = self.get_offers_for_product(id)

        if len(offers) >= 1 and offers != None:
            return offers[0][1]
        else:
            # No offers
            return None

    def get_offers_for_product(self, id):
        """Determine all offers for a product"""
        if not self.update_tradable_products():
            return None

        if self.__tradeable_product_ids != None and id in self.__tradeable_product_ids:
            return self.__http.get_offers_for_product(id)
        else:
            # Product is not tradeable
            return None

    def find_big_gap_in_offers(self, id, npc_price):
        """Determines a large gap (> 10 %) between the offers and returns it"""
        offers = self.get_offers_for_product(id)
        prices = []

        if offers == None:
            return []
        
        # Collect all prices in one list
        for element in offers:
            prices.append(element[1])

        # id != 0: Do not sort coins
        if (npc_price != None and id != 0):
            iList = range(0, len(prices))
            iList.reverse()
            for i in iList:
                if prices[i] > npc_price:
                    del prices[i]

        gaps = []
        # At least two entries are required for comparison
        if (len(prices) < 2):
            return gaps
    
        for i in range(0, len(prices)-1):
            if (((prices[i+1] / 1.1) - prices[i]) > 0.0):
                gaps.append([prices[i], prices[i+1]])
        return gaps
