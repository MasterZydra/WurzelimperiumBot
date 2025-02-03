#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.minigames.adventCalendar.AdventCalendar import AdventCalendar
from src.minigames.birthdayCalendar.BirthdayCalendar import BirthdayCalendar
from src.minigames.pumpkinDigging.PumpkinDigging import PumpkinDigging

class Minigames():

    def __init__(self):
        # TODO Enhancement: Check for games only if the current date matches the seasons the games are available.
        self.__adventCalendar = AdventCalendar()
        self.__birthdayCalendar = BirthdayCalendar()
        self.__pumpkinDigging = PumpkinDigging()

    def play(self):
        if self.__adventCalendar.is_available():
            print('Opening advent calendar...')
            self.__adventCalendar.play()

        if self.__birthdayCalendar.is_available():
            print('Opening birthday calendar...')
            self.__birthdayCalendar.play()

        if self.__pumpkinDigging.is_available():
            print('Playing pumkin digging game...')
            self.__pumpkinDigging.play()