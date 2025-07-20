#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.minigames.adventCalendar.AdventCalendar import AdventCalendar
from src.minigames.birthdayCalendar.BirthdayCalendar import BirthdayCalendar
from src.minigames.summerCalendar.SummerCalendar import SummerCalendar
from src.minigames.fair.Fair import Fair
from src.minigames.pumpkinDigging.PumpkinDigging import PumpkinDigging

class Minigames:
    def play(self):
        # TODO Enhancement: Check for games only if the current date matches the seasons the games are available.

        self.__adventCalendar = AdventCalendar()
        if self.__adventCalendar.is_available():
            print('Opening advent calendar...')
            self.__adventCalendar.play()

        self.__birthdayCalendar = BirthdayCalendar()
        if self.__birthdayCalendar.is_available():
            print('Opening birthday calendar...')
            self.__birthdayCalendar.play()

        self.__summerCalendar = SummerCalendar()
        if self.__summerCalendar.is_available():
            print('Opening summer calendar...')
            self.__summerCalendar.play()

        self.__fair = Fair()
        if self.__fair.is_available():
            print('Playing fair...')
            self.__fair.play()

        self.__pumpkinDigging = PumpkinDigging()
        if self.__pumpkinDigging.is_available():
            print('Playing pumkin digging game...')
            self.__pumpkinDigging.play()
