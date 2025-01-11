#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.HttpFeature import Http
from src.core.User import User

class Feature():
    _instance = None

    def __new__(self):
        if self._instance is None:
            self._instance = super(Feature, self).__new__(self)
            self._instance.__initClass()
        return self._instance
    
    def __initClass(self):
        self.__http = Http()

    def is_note_available(self) -> bool:
        return User().get_level() >= 3

    def is_city_park_available(self) -> bool:
        return User().get_level() >= 5

    def is_herb_garden_available(self) -> bool:
        return User().get_level() >= 10
    
    def is_aqua_garden_available(self) -> bool:
        if User().get_level() < 19:
            return False
        return self.__http.is_aqua_garden_available()

    def is_bonsai_farm_available(self) -> bool:
        if User().get_level() < 20:
            return False
        return self.__http.is_bonsai_farm_available()

    def is_honey_farm_available(self) -> bool:
        if User().get_level() < 10:
            return False
        return self.__http.is_honey_farm_available()
    
    def is_greenhouse_available(self) -> bool:
        if User().get_level() < 12:
            return False
        return self.__http.is_greenhouse_available()
