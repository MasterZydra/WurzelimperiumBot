#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Snail:
    def __init__(self, data, slot = 0, type = 0): # type: for theoretical calculation
        self.__type = type # 1-6
        self.__name = None
        self.__slot = slot # 1-6
        self.__in_race = False
        self.__energy_max = 0
        self.__loved = []
        self.__hated = []
        self.__speed = 0
        self.__sliminess = 0
        self.__daytime = None
        self.__cooldown_remain = 0
        self.__level = 0
        self.__data = data
        if type:
            self.__set_dummy_data()
        if slot:
            self.__set_snailslot_data()
        self.__set_config_data(self.__type)

    def __set_dummy_data(self):
        self.__level = 10
        self.__in_race = False
        self.__cooldown_remain = 0

    def __set_snailslot_data(self):
        self.__level = self.__data["data"]["snails"][f"{self.__slot}"]["level"]["level"]
        self.__type = self.__data.get("data").get("snails").get(f"{self.__slot}").get("type")
        self.__in_race = self.__data.get("data").get("snails").get(f"{self.__slot}").get("race")
        self.__cooldown_remain = self.__data.get("data").get("snails").get(f"{self.__slot}").get("cooldown_remain")

    def __set_config_data(self, type):
        self.__name = self.__data.get("config").get("snail").get(f"{type}").get("name")
        self.__energy_max = self.__data.get("config").get("snail_attributes").get(f"{type}").get(f"{self.__level}").get("energy")
        self.__loved = self.__data.get("config").get("snail").get(f"{type}").get("loved")
        self.__hated = self.__data.get("config").get("snail").get(f"{type}").get("hated")
        self.__speed = round(0.72 * self.__data.get("config").get("snail_attributes").get(f"{type}").get(f"{self.__level}").get("speed"), 2)
        self.__sliminess = self.__data.get("config").get("snail_attributes").get(f"{type}").get(f"{self.__level}").get("sliminess")
        self.__daytime = self.__data.get("config").get("snail").get(f"{type}").get("daytime")

    def get_loved(self):
        return self.__loved

    def get_hated(self):
        return self.__hated

    def get_speed(self):
        return self.__speed

    def get_sliminess(self):
        return self.__sliminess

    def get_daytime(self):
        return self.__daytime

    def get_slot(self):
        return self.__slot

    def get_type(self):
        return self.__type

    def get_in_race(self):
        return self.__in_race

    def get_cooldown_remain(self):
        return self.__cooldown_remain
