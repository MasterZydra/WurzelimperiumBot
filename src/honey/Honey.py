#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from collections import Counter
from src.honey.Http import Http

class Honey():
    """All important informations for the honey garden"""

    def __init__(self):
        self.__http = Http()
        self.__log = logging.getLogger('bot.Honig')
        self.__log.setLevel(logging.DEBUG)
        self.update()

    def update(self):
        self.__data = self.__http.get_honey_farm_infos()

    def start_hive(self, hive_id):
        try:
            self.__http.send_bees_2hours(hive_id)
            self._logHonig.info(f'Sending Bees from hive {hive_id=}')
            self.update()
        except:
            raise

    def start_all_hives(self):
        available_hives = self.get_available_hives()
        available_products = self.get_farm_infos()['data']['garden']
        mapping = self.get_farm_infos()['data']['config']['mapping']
        if len(available_products) == 0:
            return
        for key, value in available_hives.items():
            if str(mapping.get(value.get('pid'))['pid']) in available_products.keys():
                self.start_hive(key)

    def fill_honey(self):
        """Fill collected honey"""
        stock = self.get_farm_infos()['data']['stock']
        if isinstance(stock, list):
            stock_list = stock
        else:
            stock_list = list(stock.values())
    
        if '100000' in stock_list:
            try:
                self._http.fill_honey()
                self.update()
            except:
                raise

    def get_farm_infos(self):
        return self.__data

    def get_honey_quest_no(self):
        return self.get_farm_infos()['questnr']

    def get_honey_quest(self):
        return self.get_farm_infos()['questData']

    def get_honey_quest_products(self):
        products_list = self.get_honey_quest()['products']
        return {str(product['pid']): product['missing'] for product in products_list}

    def get_honey_wimps_data(self):
        wimps_list = self.get_farm_infos()['data']['wimps']
        wimps = {}
        for wimp in wimps_list:
            wimps[wimp['id']] = [int(wimp['price']), wimp['data']]
        return wimps

    def get_honey_wimps_products(self):
        wimps_data = self.get_honey_wimps_data()
        products = Counter()
        for value in wimps_data.values():
            products += value[1]
        return dict(products)

    def get_available_hives(self):
        hives = self.get_farm_infos()['data']['data']['hives']
        return {
            key: value for key, value in hives.items()
            if value.get('tour_remain', 0) <= 0
            and not value.get('buyable', 0)
        }

    def get_hive_types(self):
        return self.get_farm_infos()[3]

    def change_hives_type_for_quest(self):
        # TODO extend and create HTTP-Requests
        quest = self.get_honey_quest()
        for i in quest:
            if quest[i]['missing'] != 0:
                change = quest[i]['pid']
                break
            else:
                change = 315

        try:
            self.__http.change_hives_type_for_quest(change)
        except:
            raise
