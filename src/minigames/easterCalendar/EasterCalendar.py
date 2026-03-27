#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.minigames.birthdayCalendar.Http import Http
from datetime import date

class EasterCalendar:
    def __init__(self):
        self.__http = Http()

    def is_available(self, page_content: str) -> bool:
        if not self.__check_time_span():
            return False

        if 'id="calendar" class="easter long"' not in page_content:
            return False

        # Check if current day is already opened
        content = self.__http.init_game()
        if content is None:
            return False

        self.__data = content

        return 'days' in content['data']['data'] and str(self.__getFieldId()) not in content['data']['data']['days']

    def play(self) -> bool:
        if self.__http.init_game() is None:
            return False

        field_id = self.__getFieldId()
        if field_id is None:
            return False

        return self.__http.open(field_id) is not None

    def __getFieldId(self) -> int|None:
        """
        Get the field ID for today's date.
        
        Compares today's date in 'dd.mm.' format (e.g., '25.12.') against the 
        shortdate values in the configuration data to find the matching field.
        
        Returns:
            int: The field ID corresponding to today's date, or None if no match is found.
        """
        today = date.today().strftime('%d.%m.')

        for field_id, field_data in self.__data['data']['config']['fields'].items():
            if field_data['shortdate'] == today:
                return int(field_id)

        return None

    def __check_time_span(self) -> bool:
        """Check if today is between 1st march and 30th april"""
        today = date.today()
        start_date = date(today.year, 3, 1)
        end_date = date(today.year, 4, 30)
        return start_date <= today <= end_date

# Example for "self.__data":
# {
#     'status': 'ok',
#     'data': {
#         'day': 1,
#         'free': [],
#         'reward': 0,
#         'data': {
#             'remain': 1150440,
#             'days': {
#                 '1': {'time': 1775611221, 'reward': {'autoplant': 10}}
#             }
#         },
#         'config': {
#             'fields': {
#                 '1': {'reward': {'autoplant': 10}, 'date': '27.03.2026', 'shortdate': '27.03.'},
#                 '2': {'reward': {'points': 500}, 'date': '28.03.2026', 'shortdate': '28.03.'},
#             },
#             'missed_coins': 2,
#             'season': 'easter',
#             'showdate': 2
#         }
#     },
#     'init': 1
# }