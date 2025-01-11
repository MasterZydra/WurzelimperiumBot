#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.HTTPCommunication import HTTPConnection
from urllib.parse import urlencode

class Http(object):
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def buy_from_shop(self, shop: int, productId: int, amount: int = 1):
        parameter = urlencode({
            's': shop,
            'page': 1,
            'change_page_only': 0,
            'produkt[0]': productId,
            'anzahl[0]': amount
        })
        try:
            header = {'Content-Type': 'application/x-www-form-urlencoded'}
            response, content = self.__http.send(f'stadt/shop.php?s={shop}', 'POST', parameter, header)
            self.__http.check_http_state_ok(response)
        except:
            raise

    def buy_from_aqua_shop(self, productId: int, amount: int = 1):
        adresse = f'ajax/ajax.php?products={productId}:{amount}&do=shopBuyProducts&type=aqua&token={self.__http.token()}'
        try:
            response, content = self.__http.send(adresse)
            self.__http.check_http_state_ok(response)
        except:
            return ''
