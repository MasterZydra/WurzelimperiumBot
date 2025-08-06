#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.minigames.adventCalendar.Http import Http
from datetime import date

class AdventCalendar:
    def __init__(self):
        self.__http = Http()

    def is_available(self, page_content: str) -> bool:
        if not self.__check_time_span():
            return False

        if 'id="calendar" class="xmas long"' not in page_content:
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
        if today.month == 12:
            return today.day
        return today.day + 31

    def __check_time_span(self) -> bool:
        """Check if today is between 1st december and 6th january"""
        today = date.today()
        start_date = date(today.year, 1, 1)
        end_date = date(today.year, 1, 6)
        return start_date <= today <= end_date or today.month == 12