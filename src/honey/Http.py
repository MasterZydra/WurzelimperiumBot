#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.HTTPCommunication import HTTPConnection

class Http(object):
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def get_honey_farm_infos(self):
        """Get all important honey garden informations"""
        try:
            response, content = self.__http.sendRequest(f'ajax/ajax.php?do=bees_init&token={self.__http.token()}')
            self.__http.checkIfHTTPStateIsOK(response)
            content = self.__http.generateJSONContentAndCheckForOK(content)
            quest_nr = content['questnr']
            honey_quest = self.get_honey_quests(content)
            hives = self.get_available_hives(content)
            hive_type = self.get_hive_types(content)
            return quest_nr, honey_quest, hives, hive_type
        except:
            raise

    def get_honey_quests(self, content):
        """Search JSON content for available bee quests"""
        honey_quest = {}
        i = 1
        for course in content['questData']['products']:
            new = {i: {'pid': course['pid'], 'type': course['name']}}
            honey_quest.update(new)
            i = i + 1
        return honey_quest

    def get_available_hives(self, content):
        """Search JSON content for available hives"""
        available_hives = []

        for hive in content['data']['data']['hives']:
            if "blocked" not in content['data']['data']['hives'][hive]:
                available_hives.append(int(hive))

        # Sorting an empty array changes the object type to None
        if len(available_hives) > 0:
            available_hives.sort(reverse=False)

        return available_hives

    def get_hive_types(self, content):
        """Search JSON content for hive types"""
        hive_types = []

        for hive in content['data']['data']['hives']:
            if "blocked" not in content['data']['data']['hives'][hive]:
                hive_types.append(int(hive))

        # Sorting an empty array changes the object type to None
        if len(hive_types) > 0:
            hive_types.sort(reverse=False)

        return hive_types

    def fill_honey(self):
        """Fill collected honey"""
        try:
            response, content = self.__http.sendRequest(f'ajax/ajax.php?do=bees_fill&token={self.__http.token()}')
            self.__http.checkIfHTTPStateIsOK(response)
        except:
            raise

    def change_hives_type_for_quest(self, hive, quest_requirements):
        """Change hive type for quest requirements"""
        try:
            address = f'ajax/ajax.php?do=bees_changehiveproduct&id={str(hive)}&pid={str(quest_requirements)}&token={self.__http.token()}'
            response, content = self.__http.sendRequest(address)
            self.__http.checkIfHTTPStateIsOK(response)
        except:
            pass

    def send_bees_2hours(self, hive):
        """Send bees for 2 hours"""
        # TODO Check if bee is sended, sometimes 1 hive got skipped
        try:
            address = f'ajax/ajax.php?do=bees_startflight&id={str(hive)}&tour=1&token={self.__http.token()}'
            response, content = self.__http.sendRequest(address)
            self.__http.checkIfHTTPStateIsOK(response)
        except:
            pass