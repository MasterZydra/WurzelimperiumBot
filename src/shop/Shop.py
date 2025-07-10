#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.shop.Http import Http
from src.shop.ShopProducts import ShopProducts
from src.stock.Stock import Stock
from src.product.ProductData import ProductData

class Shop:
    def __init__(self):
        self.__http = Http()

    def buy(self, product_name, amount: int):
        if type(product_name) is int:
            product_name = ProductData().get_product_by_id(product_name).get_name()

        product = ProductData().get_product_by_name(product_name)
        if product is None:
            print(f'Plant "{product_name}" not found')
            return -1

        productId = product.get_id()

        shop = None
        for k, id in ShopProducts.products().items():
            if product_name in k:
                shop = id
                break
        if shop in [1,2,3,4]:
            try:
                self.__http.buy(shop, productId, amount)
            except Exception:
                pass
        elif shop == 0:
            try:
                self.__http.buy_aqua(productId, amount)
            except Exception:
                pass

        Stock().update()
        return 0
