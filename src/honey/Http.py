#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.HTTPCommunication import HTTPConnection

class Http(object):
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def get_honey_farm_info(self):
        try:
            response, content = self.__http.send(f'ajax/ajax.php?do=bees_init&token={self.__http.token()}')
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except:
            raise
        
    def pour_honey(self):
        try:
            response, content = self.__http.send(f'ajax/ajax.php?do=bees_fill&token={self.__http.token()}')
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except:
            raise 

    def change_hive_type(self, hive, pid): 
        address = f'ajax/ajax.php?do=bees_changehiveproduct&id={hive}' \
                  f'&pid={pid}&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except:
            raise

            self.__http.check_http_state_ok(response)

    def send_all_hives(self, tour):
        """parameters: tour: 1 = 2h, 2 = 8h, 3 = 24h"""
        address = f'ajax/ajax.php?do=bees_startflight_all&tour={tour}&token={self.__http.token()}'
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except:
            raise

    def send_hive(self, tour, hive):
        """parameters: tour: 1 = 2h, 2 = 8h, 3 = 24h"""
        try:
            address = f'ajax/ajax.php?do=bees_startflight&id={hive}&tour={tour}&token={self.__http.token()}'
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
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