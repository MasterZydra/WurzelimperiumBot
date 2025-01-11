#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.shop.Http import Http
from src.shop.ShopProducts import ShopProducts
from src.product.ProductData import ProductData

class Shop:
    def __init__(self):
        self.__http = Http()

    def buy_from_shop(self, product_name, amount: int):
        if type(product_name) is int:
            product_name = ProductData().get_product_by_id(product_name).get_name()

        product = ProductData().get_product_by_name(product_name)
        if product is None:
            print(f'Plant "{product_name}" not found')
            return -1

        productId = product.get_id()

        Shop = None
        for k, id in ShopProducts.products().items():
            if product_name in k:
                Shop = id
                break
        if Shop in [1,2,3,4]:
            try:
                self.__http.buy_from_shop(Shop, productId, amount)
            except:
                pass
        elif Shop == 0:
            try:
                self.__http.buy_from_aqua_shop(productId, amount)
            except:
                pass

        return 0
