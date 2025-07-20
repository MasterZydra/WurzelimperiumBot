#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.HTTPCommunication import HTTPConnection
from src.logger.Logger import Logger
from src.garden.Http import Http as HttpGarden

class Http:
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()
        self.__httpGarden = HttpGarden()

    def get_wimps_data(self, garden_id):
        """Get wimps data including wimp_id and list of products with amount"""
        if self.__httpGarden.change_garden(garden_id) is None:
            return None

        try:
            response, content = self.__http.send(f'ajax/verkaufajax.php?do=getAreaData&token={self.__http.token()}')
            self.__http.check_http_state_ok(response)
            jContent = self.__http.get_json_and_check_for_ok(content)
            return self.__find_wimps_data_from_json(jContent)
        except Exception:
            Logger().print_exception("Failed to get wimps data")
            return None

    def get_wimps_data_watergarden(self):
        """Get wimps data including wimp_id and list of products with amount"""
        address = f'ajax/ajax.php?do=watergardenGetGarden&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            jContent = self.__http.get_json_and_check_for_ok(content)
            return self.__find_wimps_data_from_json(jContent)
        except Exception:
            Logger().print_exception("Failed to get watergarden wimps data")
            return None

    def __find_wimps_data_from_json(self, jContent):
        """Returns list of growing plants from JSON content"""
        wimpsData = {}
        for wimp in jContent['wimps']:
            product_data = {}
            wimp_id = wimp['sheet']['id']
            cash = wimp['sheet']['sum']
            for product in wimp['sheet']['products']:
                product_data[str(product['pid'])] = int(product['amount'])
            wimpsData[wimp_id] = [cash, product_data]
        return wimpsData

    def sell_to_wimp(self, wimp_id):
        """
        Sell products to wimp with a given id
        @param wimp_id: str
        @return: dict of new balance of sold products
        """
        try:
            address = f'ajax/verkaufajax.php?do=accept&id={wimp_id}&token={self.__http.token()}'
            response, content = self.__http.send(address, 'POST')
            self.__http.check_http_state_ok(response)
            jContent = self.__http.get_json_and_check_for_ok(content)
            return jContent['newProductCounts']
        except Exception:
            Logger().print_exception("Failed to sell to wimp")
            return None

    def decline_wimp(self, wimp_id):
        """
        Decline wimp with a given id
        @param wimp_id: str
        @return: 'decline'
        """
        try:
            address = f'ajax/verkaufajax.php?do=decline&id={wimp_id}&token={self.__http.token()}'
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            jContent = self.__http.get_json_and_check_for_ok(content)
            return jContent['action']
        except Exception:
            Logger().print_exception("Failed to decline wimp")
            return None