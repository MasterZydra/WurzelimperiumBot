#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.HTTPCommunication import HTTPConnection
from src.logger.Logger import Logger
from urllib.parse import urlencode

class Http:
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def buy(self, shop: int, productId: int, amount: int = 1) -> bool:
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
            return True
        except Exception:
            Logger().print_exception(f"Failed to buy product {productId} {amount} times")
            return False

    def buy_aqua(self, productId: int, amount: int = 1) -> bool:
        adresse = f'ajax/ajax.php?products={productId}:{amount}&do=shopBuyProducts&type=aqua&token={self.__http.token()}'
        try:
            response, content = self.__http.send(adresse)
            self.__http.check_http_state_ok(response)
            return True
        except Exception:
            Logger().print_exception(f"Failed to buy aqua product {productId} {amount} times")
            return False
