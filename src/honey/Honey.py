#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from collections import Counter
from src.core.User import User
from src.honey.Hive import Hive
from src.honey.Http import Http

class Honey():
    """All important informations for the honey garden"""

    def __init__(self):
        self.__http = Http()
        self.__user = User()
        self.__log = logging.getLogger('bot.Honig')
        self.__log.setLevel(logging.DEBUG)
        self.__data = None
        self.__unlocked_hives = None
        self.__honey_types = None
        self.update()

    def update(self):
        self.__set_data(self.__http.get_honey_farm_info())

    def start_tour(self, tour: int):
        """@param tour: 1 = 2h, 2 = 8h, 3 = 24h"""
        if self.__user.is_premium_active():
            self.__set_data(self.__http.send_all_hives(tour))
        else:
            hives = self.get_available_hives()
            if hives is False:
                return
            hive: Hive
            for hive in hives:
                self.__set_data(self.__http.send_hive(tour, hive.get_nr()))

    def get_available_hives(self):
        available_products = self.__data['data']['garden']
        if len(available_products) == 0:
            return False

        hives = []
        hive: Hive
        for hive in self.__unlocked_hives:
            if hive.get_tour_remain() <= 0 and hive.get_pid() in [self.__get_honeyID_from_productID(pid) for pid in available_products]:
                hives.append(hive)
        return hives

    def check_start_hives(self):
        hives = self.get_available_hives()
        if hives is False:
            return False
        return len(hives) > 0

    def check_pour_honey(self):
        stock = self.__data['data']['stock']
        for key, value in stock.items():
            stock.update({key: int(value)})

        transfer_stock = {}
        if {key: value for key, value in stock.items() if value >= 100000}:
            content = self.__http.pour_honey()
            self.__set_data(content)
            transfer_stock = self.__data['data']['transfer_stock'] #honey-pid, and count
        return transfer_stock

    def change_all_hives_types(self, product_ID):
        pid = product_ID
        honey_pid = self.__honey_types[f'{pid}']

        hive: Hive
        for hive in self.__unlocked_hives:
            if hive.get_pid_change_remain() < 0 and hive.get_pid() is not honey_pid:
                jContent = self.__http.change_hive_type(hive.get_nr(), honey_pid)
                self.__set_data(jContent)
        self.__log.info(f"Changed all hive types to: {honey_pid}")

    # Wimps

    def get_wimps_data(self):
        wimps_list = self.__data['data']['wimps']
        wimps = {}
        for wimp in wimps_list:
            wimps[wimp['id']] = [int(wimp['price']), wimp['data']]
        return wimps

    def get_honey_wimps_products(self):
        wimps_data = self.get_wimps_data()
        products = Counter()
        for value in wimps_data.values():
            products += value[1]
        return dict(products)

    # Quest

    def get_honey_quest_no(self):
        return self.__data['questnr']

    def get_honey_quest(self):
        return self.__data['questData']

    def get_honey_quest_products(self):
        products_list = self.get_honey_quest()['products']
        return {str(product['pid']): product['missing'] for product in products_list}

    # Internal helper functions

    def __set_data(self, data):
        if not 'questnr' in data:
            self.__data['data'] = data['data']
        else:
            self.__data = data

        self.__unlocked_hives = self.__get_hives_unlocked()
        self.__honey_types = self.__get_dict_product_for_honey_pid()

    def __get_hives_unlocked(self):
        """Returns a list with the unlocked hives as objects"""
        hives = self.__data['data']['data']['hives']
        unlocked_hives = []
        for key, value in hives.items():
            if not 'buyable' in value.keys():
                unlocked_hives.append(Hive(key, value))
        return unlocked_hives

    def __get_dict_product_for_honey_pid(self):
        honey_pids = self.__data['data']['config']['mapping']
        honey_products = {}
        for key, value in honey_pids.items():
            honey_products.update({str(value.get('pid')): key})
        return honey_products

    def __get_honeyID_from_productID(self, pid):
        return self.__honey_types[f'{pid}']