#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 23.01.2019

@author: MrFlamez
'''

import datetime
from src.logger.Logger import Logger

CATEGORY_DECORATION       = 'd'
CATEGORY_HERBS            = 'h'
CATEGORY_HONEY            = 'honey'
CATEGORY_WATER_PLANTS     = 'w'
CATEGORY_VEGETABLES       = 'v'
CATEGORY_WATER_DECORATION = 'wd'
CATEGORY_COINS            = ''
CATEGORY_ADORNMENTS       = 'z'
CATEGORY_OTHER            = 'u'

class Product:
    def __init__(self, id, cat, sx, sy, name, lvl, crop, plantable, time, edge):
        self.__id = id
        self.__category = cat
        self.__sx = sx
        self.__sy = sy
        self.__name = name.decode('UTF-8')
        self.__level = lvl
        self.__crop = crop
        self.__is_plantable = plantable
        self.__time_until_harvest = time
        self.__edge = edge
        self.__price_NPC = None

    def get_id(self):
        return self.__id

    def get_category(self):
        return self.__category

    def get_crop(self):
        return self.__crop

    def get_name(self):
        return self.__name

    def get_sx(self):
        return self.__sx

    def get_sy(self):
        return self.__sy

    def get_edge(self):
        return self.__edge

    def get_price_npc(self):
        return self.__price_NPC

    def get_growing_time(self):
        return self.__time_until_harvest

    def get_level(self):
        return self.__level

    def is_plantable(self):
        return self.__is_plantable

    def is_vegetable(self):
        return self.get_category() == CATEGORY_VEGETABLES and not self.get_price_npc() is None

    def is_water_plant(self):
        return self.get_category() == CATEGORY_WATER_PLANTS

    def is_decoration(self):
        return self.get_category() == CATEGORY_DECORATION or self.get_category() == CATEGORY_WATER_DECORATION

    def set_price_npc(self, price):
        self.__price_NPC = price

    def print_all(self):
        # Show empty string instead of "None"
        xstr = lambda s: s or ""

        Logger.print('ID:', str(self.__id).rjust(3), ' ', \
              'CAT:', str(self.__category).ljust(5), ' ', \
              'Name:', str(self.__name).ljust(35), ' ', \
              'Plantable:', str(self.__is_plantable).ljust(5), ' ', \
              'NPC:', str(xstr(self.__price_NPC)).rjust(6), ' ', \
              'Time:', str(str(datetime.timedelta(seconds=self.__time_until_harvest))).rjust(8), ' ', \
              'SX:', str(xstr(self.__sx)), ' ', \
              'SY:', str(xstr(self.__sy)))

