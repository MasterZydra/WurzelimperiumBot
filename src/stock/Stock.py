#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.stock.Http import Http

class Stock:
    _instance = None

    def __new__(self):
        if self._instance is None:
            self._instance = super(Stock, self).__new__(self)
            self._instance.__initClass()
        return self._instance
    
    def __initClass(self):
        self.__http = Http()
        self.__products = {}

    def init_product_list(self, product_list):
        for product_id in product_list:
            self.__products[str(product_id)] = 0

    def update(self) -> bool:
        """Updates the stock for all products"""
        # Reset before updating
        for product_id in self.__products.keys():
            self.__products[product_id] = 0

        inventory = self.__http.get_inventory()
        if inventory is None:
            return False
        for i in inventory:
            self.__products[i] = inventory[i]
        return True

    def get_stock_by_product_id(self, product_id):
        return self.__products[str(product_id)]

    def get_keys(self):
        return self.__products.keys()

    def get_ordered_stock_list(self, filter_zero: bool = True):
        sortedStock = dict(sorted(self.__products.items(), key=lambda item: item[1]))
        filteredStock = dict()
        for productID in sortedStock:
            if filter_zero and sortedStock[str(productID)] == 0: continue
            filteredStock[str(productID)] = sortedStock[str(productID)]
        return filteredStock

    def get_lowest_stock_entry(self):
        for productID in self.get_ordered_stock_list().keys():
            return productID
        return -1
