#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 23.05.2019

@author: MrFlamez
'''

import json
from src.product.Http import Http
from src.product.Product import Product

class ProductData:
    _instance = None

    def __new__(self):
        if self._instance is None:
            self._instance = super(ProductData, self).__new__(self)
            self._instance.__initClass()
        return self._instance
    
    def __initClass(self):
        self.__http = Http()
        self.__products = []

    def __set_all_prices(self):
        """Determine all NPC prices and set them for every product"""
        prices = self.__http.get_npc_prices()

        product: Product
        for product in self.__products:
            product_name = product.get_name()
            if product_name in prices.keys():
                product.set_price_npc(prices[product_name])

        # Set value for Coin manually because it is not listed in the table
        self.get_product_by_id(0).set_price_npc(300.0)

    def get_product_by_id(self, id):
        product: Product
        for product in self.__products:
            if int(id) == int(product.get_id()): return product
        return None

    def get_product_by_name(self, name : str):
        product: Product
        for product in self.__products:
            if (name.lower() == product.get_name().lower()): return product
        return None

    def get_product_id_list(self):
        ids = []
        product: Product
        for product in self.__products:
            id = product.get_id()
            ids.append(id)

        return ids

    def get_single_field_vegetable_list(self):
        plants = []
        product: Product
        for product in self.__products:
            if product.get_sx() != 1 or product.get_sy() != 1 \
            or not product.is_vegetable() or not product.is_plantable():
                continue

            plants.append(product.get_name())

        return plants

    def init(self):
        """Initialize all products"""
        products = dict(json.loads(self.__http.get_all_product_infos()))
        keys = sorted(products.keys())

        # Unused attributes: img, imgPhase, fileext, clear, edge, pieces, speedup_cooldown in Kategorie z
        for key in keys:
            # 999 is only a test entry and is not used
            if key == '999':
                continue

            sx = 0
            sy = 0
            if 'sx' in products[key]:
                sx = products[key]['sx']
            if 'sy' in products[key]:
                sy = products[key]['sy']

            name = products[key]['name'].replace('&nbsp;', ' ')
            self.__products.append(Product(
                id        = int(key), \
                cat       = products[key]['category'], \
                sx        = sx, \
                sy        = sy, \
                name      = name.encode('utf-8'), \
                lvl       = products[key]['level'], \
                crop      = products[key]['crop'], \
                plantable = products[key]['plantable'], \
                time      = products[key]['time'], \
                edge      = products[key]['edge']
            ))

        self.__set_all_prices()

    def print_all(self):
        sorted_products = sorted(self.__products, key=lambda x:x.get_name().lower())
        product: Product
        for product in sorted_products:
            product.print_all()

    def print_all_vegetables(self):
        sorted_products = sorted(self.__products, key=lambda x:x.get_name().lower())
        product: Product
        for product in sorted_products:
            if not product.is_vegetable():
                continue
            product.print_all()

    def print_all_water_plants(self):
        sorted_products = sorted(self.__products, key=lambda x:x.get_name().lower())
        product: Product
        for product in sorted_products:
            if not product.is_water_plant():
                continue
            product.print_all()
