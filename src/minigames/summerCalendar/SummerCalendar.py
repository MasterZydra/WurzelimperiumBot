#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.minigames.summerCalendar.Http import Http
from datetime import date

class SummerCalendar:
    def __init__(self):
        self.__http = Http()

    def is_available(self, page_content: str) -> bool:
        if not self.__check_time_span():
            return False

        if 'id="calendar" class="summer short"' not in page_content:
            return False

        # Check if current day is already opened
        content = self.__http.init_game()
        if content is None:
            return False
        return 'days' in content['data']['data'] and str(self.__getFieldId()) not in content['data']['data']['days']

    def play(self) -> bool:
        if self.__http.init_game() is None:
            return False
        return self.__http.open(self.__getFieldId()) is not None

    def __getFieldId(self) -> int:
        today = date.today()
        return today.day

    def __check_time_span(self) -> bool:
        """Check if today is between 1st July and 31th July"""
        today = date.today()
        return today.month == 7