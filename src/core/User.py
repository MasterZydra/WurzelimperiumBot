#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.HttpUser import Http
import html

class User():
    _instance = None

    def __new__(self):
        if self._instance is None:
            self._instance = super(User, self).__new__(self)
            self._instance.__initClass()
        return self._instance
    
    def __initClass(self):
        self.accountLogin = None
        self.__http = Http()
        self.__data = None
        self.__number_of_gardens = None
        self.__user_id = None
        self.__is_mail_confirmed = None
        self.__has_watering_gnome_helper = None

    def update(self, only_data = False):
        """Get user data from server and save in this class"""
        try:
            self.__data = self.__http.load_data()
            if only_data:
                return

            self.__number_of_gardens = self.__http.get_info_from_stats("Gardens")
            self.__user_id = self.__http.get_user_id()
            self.__is_mail_confirmed = self.__http.check_mail_confirmed()
            self.__has_watering_gnome_helper = self.__http.has_watering_gnome_helper()
        except:
            print('Could not load the user data')

    def get_user_id(self) -> str:
        return self.__user_id

    def get_username(self) -> str:
        return self.__data['uname']

    def get_level(self) -> int:
        return self.__data['levelnr']

    def get_level_name(self) -> str:
        return html.unescape(self.__data['level'])

    def get_coins(self) -> int:
        return self.__data['coins']

    def get_points(self) -> int:
        return self.__data['points']

    def get_bar(self) -> float:
        return self.__data['bar_unformat']

    def get_bar_formatted(self) -> str:
        return self.__data['bar']

    def is_premium_active(self) -> bool:
        return self.__data['citymap']['premium'] == "1"

    def is_guild_member(self) -> bool:
        return self.__data['g_tag'] != ""

    def get_time(self) -> int:
        return self.__data['time']

    def get_number_of_gardens(self) -> int:
        return self.__number_of_gardens

    def is_mail_confirmed(self) -> bool:
        return self.__is_mail_confirmed

    def has_watering_gnome_helper(self) -> bool:
        return self.__has_watering_gnome_helper