#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.HTTPCommunication import HTTPConnection
from src.logger.Logger import Logger
from src.minigames.adventCalendar.AdventCalendar import AdventCalendar
from src.minigames.birthdayCalendar.BirthdayCalendar import BirthdayCalendar
from src.minigames.easterDigging.EasterDigging import EasterDigging
from src.minigames.easterCalendar.EasterCalendar import EasterCalendar
from src.minigames.fair.Fair import Fair
from src.minigames.pumpkinDigging.PumpkinDigging import PumpkinDigging
from src.minigames.summerCalendar.SummerCalendar import SummerCalendar
from src.minigames.summerMemory.SummerMemory import SummerMemory


class Minigames:
    def play(self, allowed_events: list = ['all', 'advent_calendar', 'birthday_calendar', 'easter_calendar', 'summer_calendar', 'easter_digging', 'pumpkin_digging', 'fair', 'summer_memory']) -> bool:
        """
        Args:
            allowed_events (list): all, advent_calendar, birthday_calendar, easter_calendar, summer_calendar, easter_digging, pumpkin_digging, fair, summer_memory.
        """
        # Get page content only once to reduce the amount of page loads
        content = self.__get_content()
        if content is None:
            return False

        # TODO Enhancement: Check for games only if the current date matches the seasons the games are available.

        # Events

        # - Calendar

        if 'all' in allowed_events or 'advent_calendar' in allowed_events:
            self.__adventCalendar = AdventCalendar()
            if self.__adventCalendar.is_available(content):
                Logger().print('Opening advent calendar...')
                self.__adventCalendar.play()

        if 'all' in allowed_events or 'birthday_calendar' in allowed_events:
            self.__birthdayCalendar = BirthdayCalendar()
            if self.__birthdayCalendar.is_available(content):
                Logger().print('Opening birthday calendar...')
                self.__birthdayCalendar.play()

        if 'all' in allowed_events or 'easter_calendar' in allowed_events: 
            self.__easterCalendar = EasterCalendar()
            if self.__easterCalendar.is_available(content):
                Logger().print('Opening easter calendar...')
                self.__easterCalendar.play()

        if 'all' in allowed_events or 'summer_calendar' in allowed_events: 
            self.__summerCalendar = SummerCalendar()
            if self.__summerCalendar.is_available(content):
                Logger().print('Opening summer calendar...')
                self.__summerCalendar.play()

        # - Digging

        if 'all' in allowed_events or 'easter_digging' in allowed_events: 
            self.__easterDigging = EasterDigging()
            if self.__easterDigging.is_available(content):
                Logger().print('Playing easter digging game...')
                self.__easterDigging.play()

        if 'all' in allowed_events or 'pumpkin_digging' in allowed_events: 
            self.__pumpkinDigging = PumpkinDigging()
            if self.__pumpkinDigging.is_available(content):
                Logger().print('Playing pumkin digging game...')
                self.__pumpkinDigging.play()

        # - Other

        if 'all' in allowed_events or 'summer_memory' in allowed_events: 
            self.__summerMemory = SummerMemory()
            if self.__summerMemory.is_available(content):
                Logger().print('Playing summer memory...')
                self.__summerMemory.play()

        if 'all' in allowed_events or 'fair' in allowed_events: 
            self.__fair = Fair()
            if self.__fair.is_available(content):
                Logger().print('Playing fair...')
                self.__fair.play()

        return True

    def __get_content(self) -> str|None:
        try:
            http: HTTPConnection = HTTPConnection()
            response, content = http.send('main.php?page=garden')
            content = content.decode('UTF-8')
            http.update_token_from_content(content)
            http.check_http_state_ok(response)
            return content
        except Exception:
            Logger().print_exception('Failed to get main page')
            return None