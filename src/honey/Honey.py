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
        self.__set_honey_farm_info(self.__http.get_honey_farm_info())
        self.__honey_types = self.__get_dict_product_for_honey_pid()
    
    def __set_honey_farm_info(self, jContent):
        self.__jContent_data = jContent['data']
        self.__unlocked_hives = self.__get_hives_unlocked()

    def __get_hives_unlocked(self):
        """returns a list with the unlocked hives as objects"""
        hives = self.__jContent_data['data']['hives']
        unlocked_hives = []
        for key, value in hives.items():
            if not 'buyable' in value.keys():
                unlocked_hives.append(Hive(key, value))
        return unlocked_hives

    def __get_dict_product_for_honey_pid(self):
        honey_pids = self.__jContent_data['config']['mapping']
        honey_products = {}
        for key, value in honey_pids.items():
            honey_products.update({str(value.get('pid')): key})
        return honey_products
    
    def __get_honeyID_from_productID(self, pid):
        return self.__honey_types[f'{pid}']

    def start_tour(self, tour: int):
        jContent = self.__http.send_bees(tour)
        self.__set_honey_farm_info(jContent)

    def check_start_hives(self):
        available_products = self.__jContent_data['garden']
        if len(available_products) == 0:
            return False

        hive: Hive
        for hive in self.__unlocked_hives:
            if hive.get_tour_remain() <= 0 and hive.get_pid() in [self.__get_honeyID_from_productID(pid) for pid in available_products]:
                return True
        return False

    def check_pour_honey(self):
        stock = self.__jContent_data['stock']
        for key, value in stock.items():
            stock.update({key: int(value)})

        transfer_stock = {}
        if {key: value for key, value in stock.items() if value > 100000}:
            jContent = self.__http.pour_honey()
            self.__set_honey_farm_info(jContent)
            transfer_stock = self.__jContent_data['transfer_stock'] #honey-pid, and count
        return transfer_stock

    def change_all_hives_types(self, product_ID):
        pid = product_ID
        honey_pid = self.__honey_types[f'{pid}']

        hive: Hive
        for hive in self.__unlocked_hives:
            if hive.get_pid_change_remain() < 0 and hive.get_pid() is not honey_pid:
                jContent = self.__http.change_hive_type(hive.get_nr(), honey_pid)
        self.__set_honey_farm_info(jContent)
        self.__log.info(f"Changed all hive types to: {honey_pid}")

    # TODO: Wimps
    def get_honey_wimps_data(self):
        wimps_list = self.__jContent_data['wimps']
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

    # TODO: implememet Quests properly
    def get_honey_quest_no(self):
        self.__honeyquestnr = self.getQuestHoneyNr()

    def setHoneyQuest(self, http):
        """Liest die aktuelle HoneyQuest aus und speichert ihn in der Klasse."""
        self.__honeyquest = self.getQuestHoneyProducts()

    def getQuestHoneyNr(self):
        return self.getHoneyFarmInfo()['questnr']

    def getQuestHoney(self):
        return self.getHoneyFarmInfo()['questData']

    def getQuestHoneyProducts(self):
        products_list = self.getQuestHoney()['products']
        products = {str(product['pid']): product['missing'] for product in products_list}
        return products


class Hive():
    def __init__(self, nr, attributes):
        self.__nr = nr
        self.__level = attributes.get('level')
        self.__time = attributes.get('time')
        self.__pid = attributes.get('pid')
        self.__pid_change_time = attributes.get('pid_change_time')
        self.__pid_change_duration= attributes.get('pid_change_duration')
        self.__pid_change_remain = attributes.get('pid_change_remain')
        self.__tour_start = attributes.get('tour_start')
        self.__tour_duration = attributes.get('tour_duration')
        self.__tour_remain = attributes.get('tour_remain')

    def get_nr(self):
        return self.__nr

    def get_pid(self):
        return self.__pid

    def get_pid_change_remain(self):
        return self.__pid_change_remain
    
    def get_tour_remain(self):
        return self.__tour_remain
