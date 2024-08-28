#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.minigames.pumpkinDigging.PumpkinDigging import PumpkinDigging

class Minigames():

    def __init__(self):
        # TODO Enhancement: Check for games only if the current date matches the seasons the games are available.
        self.__pumpkinDigging = PumpkinDigging()

    def play(self):
        if self.__pumpkinDigging.is_available():
            print('Playing pumkin digging game...')
            self.__pumpkinDigging.play()