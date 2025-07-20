#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.greenhouse.Http import Http
from src.logger.Logger import Logger

class Greenhouse:
    """All important information for the greenhouse"""

    def __init__(self):
        self.__http = Http()
        self.__set_fields(self.__http.init_greenhouse())
        self.__care = {'fertilizer': 'a1', 'water': 'a3', 'light': 'a5', 'love': 'a7'}

    def __set_fields(self, jContent) -> bool:
        if jContent is None:
            return False
        self.__fields = jContent.get('fields', None)
        self.__fields_available = jContent.get('fieldsavailable', None)
        return True

    def do_all_cactus_care(self) -> bool:
        #time values get updated when a cactus care is performed --> may have to run method twice for up to date result
        for field, values in self.__fields.items():
            remain_time = values.get('growthtime') - values.get('elapsed')
            Logger().print(f"Cactus {field}: remaintime is {remain_time} s")

            for key, value in values.get('bars').items():
                if value < remain_time:
                    jContent = self.__http.do_cactus_care(self.__care.get(key), field)
                    if jContent is None:
                        return False
                    if jContent.get('status', 0) == 'SUCCESS':
                        self.__set_fields(jContent)
                        cost = jContent.get('price').replace('&nbsp;', ' ')
                        Logger().print(f"Cactus {field}: {key} for {cost}")
                    elif jContent.get('status', 0) == 'ERROR':
                        Logger().print_error(jContent.get('error'))

        return True

    #TODO: add method do find cheapest combination for certain cactus quality