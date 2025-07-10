#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.minigames.birthdayCalendar.Http import Http
from datetime import date

class BirthdayCalendar:
    def __init__(self):
        self.__http = Http()

    def is_available(self) -> bool:
        if not self.__check_time_span():
            return False

        if not self.__http.game_available():
            return False

        # Check if current day is already opened
        content = self.__http.init_game()
        return 'days' in content['data']['data'] and str(self.__getFieldId()) not in content['data']['data']['days']

    def play(self):
        self.__http.init_game()
        self.__http.open(self.__getFieldId())

    def __getFieldId(self) -> int:
        return date.today().day

    def __check_time_span(self) -> bool:
        """Check if today is between 1st february and 10th february"""
        today = date.today()
        start_date = date(today.year, 2, 1)
        end_date = date(today.year, 2, 10)
        return start_date <= today <= end_date