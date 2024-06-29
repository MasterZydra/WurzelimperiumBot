#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.honey.Http import Http

class Honey():
    """All important informations for the honey garden"""

    def __init__(self):
        self.__http = Http()

    def send_bees(self):
        """Send bees of all hives"""
        hives = self.get_available_hives()
        for hive in hives:
            self.__http.send_bees_2hours(hive)
            self.fill_honey()

    def fill_honey(self):
        """Fill collected honey"""
        try:
            self.__http.fill_honey()
        except:
            raise

    def get_honey_quest_no(self):
        return self.__http.get_honey_farm_infos()[0]

    def get_honey_quest(self):
        return self.__http.get_honey_farm_infos()[1]

    def get_available_hives(self):
        return self.__http.get_honey_farm_infos()[2]

    def get_hive_types(self):
        return self.__http.get_honey_farm_infos()[3]

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
