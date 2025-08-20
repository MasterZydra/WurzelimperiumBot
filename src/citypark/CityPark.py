#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.citypark.Http import Http
from src.logger.Logger import Logger

class CityPark:
    def __init__(self):
        self.__http = Http()
        self.__set_park_data(self.__http.init_park())

    def __set_park_data(self, content) -> bool:
        """Set the relevant park data from the JSON content"""
        if content is None:
            return False
        self.__data = content['data']
        self.__cashpoint = content["data"]["data"]["cashpoint"]
        return True

    def collect_cash(self) -> bool:
        """Collect rewards from cashpoint if there are any"""
        if not self.__data['data']["cashpoint"]["money"] > 0:
            Logger().print_error("The Cashpoint is empty.")
        else:
            content = self.__http.collect_cash_point()
            if content is None:
                return False
            Logger().print("Collected: {points} points, {money} wT, {parkpoints} parkpoints".format(points = self.__cashpoint["points"], money = self.__cashpoint["money"], parkpoints=self.__cashpoint["parkpoints"]))
            self.__set_park_data(content)
        return True

    def __get_all_deco(self, park_id=1):
        """get all items"""
        items = self.__data["data"]["park"][str(park_id)]["items"]
        all_items = {}
        for key, value in items.items():
            if 'parent' in value: 
                continue
            all_items.update({key:value})
        Logger().print("count of all park items: {}".format(len(all_items)))
        return all_items

    def __get_expired_deco(self, park_id=1):
        """get all expired items"""
        items = self.__data["data"]["park"][str(park_id)]["items"]
        renewable_items = {}
        for key, value in items.items():
            if 'parent' in value: 
                continue
            if value["remain"] < 0:
                renewable_items.update({key:value})
        Logger().info("renewable items: {}".format(len(renewable_items)))
        return renewable_items

    def renew_all_items(self) -> bool:
        """renew all expired items"""
        renewable_items = self.__get_expired_deco()
        for itemID in renewable_items.keys():
            content = self.__http.renew_item(itemID)
            if content is None:
                return False
            self.__set_park_data(content)
        Logger().print("Renewed {} Items.".format(len(renewable_items)))
        return True

    def remove_all_items(self) -> bool:
        all_items = self.__get_all_deco()
        for itemID in all_items.keys():
            content = self.__http.remove_item(itemID)
            if content is None:
                return False
            self.__set_park_data(content)
        Logger().print("Removed {} Items.".format(len(all_items)))
        return True
