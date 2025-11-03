#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.ivyhouse.Http import Http
from src.ivyhouse.ShopProduct import *
from src.logger.Logger import Logger

class Ivyhouse():
    """Wrapper for the ivyhouse"""

    def __init__(self):
        self.__http = Http()
        self.__update(self.__http.init())

    def __update(self, jContent):
        self.__data = jContent['data']['data']
        self.__breed = self.__data["breed"]
        self.__items = self.__data["items"]

        if "rewards" in jContent['data']:
            Logger().print("### REWARDS")
            Logger().print(f'{jContent['data']['rewards']}')
            if self.__breed:
                Logger().print(self.__breed.get("daily", "no daily found"))

    def __remove_pest(self):
        if self.__breed and self.__breed["pest"]:
            for name, occurrence in self.__breed["pest"].items():
                if occurrence:
                    self.__http.remove_pest(name=name, pos=1) #TODO: pos anhängig von list?!

    def __check_weather(self):
        weather = self.__breed["weather"].get("name", None)
        weather_name = WEATHER.get(weather, 0)
        weather_remain = self.__breed["weather"].get("remain", -1)
        weather_item = self.__breed["weather"].get("item", 0)
        weather_item_name = self.__search_item_name(weather_item)
        weather_item_remain = self.__breed["weather"].get("itemremain", -1)
        
        if not weather_item: #kein Item vorher platziert (z.B. Zuchtstart)
            self.__set_weather(weather_name)

        if weather_item and (not weather_name == weather_item_name or weather_item_remain < 0): #anderes Wetter OR abgelaufen
            Logger().print("remove Weather")
            content = self.__http.remove_weather()
            self.__update(content)
            self.__set_weather(weather_name)

    def __set_weather(self, weather_name) -> None:
            item_id = self.__search_item_id(weather_name)
            if not item_id:
                Logger().print("BUY WEATHER")
                if weather_name:
                    Logger().print(f"would buy: {weather_name}")
                    content = self.__http.buy_item(name=weather_name, slot=1, amount=1)
                    self.__update(content)
                    item_id = self.__search_item_id(weather_name)
            Logger().print("###SET WEATHER###")
            weather_id = item_id
            content = self.__http.set_weather(id=weather_id)
            self.__update(content)

    def __search_item_id(self, name):
        id = 0
        values = self.__items.values()

        for listitem in values:
            item_name = listitem.get("name", 0)
            id = listitem.get("id", 0)
            instock = listitem.get("instock", 0)
            if item_name == name and instock == "1":
                return id

    def __search_item_name(self, id):
        item_name = ""
        values = self.__items.values()

        for listitem in values:
            item_name = listitem.get("name", 0)
            item_id = listitem.get("id", 0)
            if item_id == id:
                return item_name

    def __check_deco(self, deco_name=DECO.get("Fenster")):
        deco_slots: dict = self.__breed.get("deco") #dict-dict
        if not deco_slots:
            deco_slots = {} #no deco in use

        slot: int
        deco: dict
        used_slots = []
        deco_data = []
        for slot, deco in deco_slots.items():
            used_slots.append(int(slot))
            deco_data.append(deco)

        available_deco_slots = self.__get_deco_slots()
        for slot in range(1, available_deco_slots+1):
            if slot in used_slots:
                print(slot)
                #check remain
                deco_remain = deco_slots.get(str(slot)).get("remain")
                if deco_remain > 0:
                    continue
                if deco_remain <= 0:
                    content = self.__http.remove_deco(slot)
                    self.__update(content)

            Logger().print("###CHECK DECO###")
            Logger().print(deco_name)

            deco_id = self.__search_item_id(name=deco_name)
            if not deco_id:
                Logger().print("###BUY DECO")
                content = self.__http.buy_item(name=deco_name, slot=1, amount=1)
                self.__update(content)

            deco_id = self.__search_item_id(name=deco_name)
            if deco_id:
                Logger().print("###SET DECO")
                content = self.__http.set_deco(slot=slot, id=deco_id)
                self.__update(content)

    def __get_deco_slots(self) -> int:
        level = self.__data.get("level", 0)
        deco_slots = 1
        if level >= 2:
            deco_slots += 1
        if level >= 5:
            deco_slots += 1
        if level >= 10:
            deco_slots += 1
        return deco_slots

    def check_breed(self, slot):
        if self.__breed: #breed=0 if breed finished
            if self.__breed.get("remain", 0) < 0: 
                Logger().print("### FINISHED")
                content = self.__http.finish_breed()
                rewards = content["data"]["rewards"]
                self.__update(content)

        if self.__breed == 0:
            Logger().print("### START")
            if slot:
                content = self.__http.start_breed(slot)
                self.__update(content)
            else:
                Logger().print("No ivy type specified!")
                return
        #remain > 0
        self.__remove_pest()
        self.__check_weather()
        self.__check_deco()
