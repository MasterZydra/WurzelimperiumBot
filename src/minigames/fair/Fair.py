#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time
from src.minigames.fair.Http import Http
from src.minigames.fair.Thimblerig import Thimblerig
from src.minigames.fair.Wetgnome import Wetgnome

REWARD_MAX = 300

class Fair:
    def __init__(self):
        self.__http = Http()

    def __init_game(self):
        self._logFair = logging.getLogger('bot.Fair')
        self._logFair.setLevel(logging.DEBUG)
        data = self.__http.init_game()
        self.__set_data(data)
        self.__thimblerig = Thimblerig(data)
        self.__wetgnome = Wetgnome(data)

    def is_available(self) -> bool:
        return self.__http.game_available()

    def play(self) -> bool:
        self.__init_game()
        if self.__http.init_game() is None:
            return False
        if not self.craft_tickets():
            return False
        if not self.play_thimblerig():
            return False
        return self.play_wetgnome()

    def __set_data(self, data):
        self.__data = data["data"]
        self.__points = self.__data['data']['points']
        self.__tickets = self.__data['data']['tickets']
        self.__ticketcost = self.__data['config']['ticketcost']
        self.__thimblerig_round = self.__data['thimblerig']['data']['round']
        self.__thimblerig_points = self.__data['thimblerig']['data']['points']
        self.__thimblerig_maxrounds = self.__data['thimblerig']['config']['maxrounds']
        self.__wetgnome_round = self.__data['wetgnome']['data']['round']
        self.__wetgnome_points = self.__data['wetgnome']['data']['points']
        self.__wetgnome_maxrounds = self.__data['wetgnome']['config']['maxrounds']

    def craft_tickets(self) -> bool:
        msg = f"{self.__points} points available. A ticket costs {self.__ticketcost} points."
        if self.__points >= self.__ticketcost:
            data = self.__http.craft_ticket()
            if data is None:
                return False
            self.__set_data(data)
            msg = f"Crafted {int(self.__points/self.__ticketcost)} tickets."
        msg += f"\nYou have {self.__tickets}x tickets in stock."
        self._logFair.info(msg)
        return True

    def play_thimblerig(self) -> bool:
        self._logFair.info(f"Thimblerig: {self.__thimblerig.get_points()}/300 balloons.")
        while self.__tickets > 0:
            if self.__thimblerig_points >= REWARD_MAX:
                self._logFair.info("Thimblerig already finished!")
                return

            if not self.__data["thimblerig"]["data"].get("wait", 0):
                if not self.__pay_ticket_thimblerig():
                    return False

            while 1 <= self.__thimblerig_round <= self.__thimblerig_maxrounds:
                if not self.__data["thimblerig"]["data"].get("wait", 0):
                    self.__thimblerig_round = self.__thimblerig.start(self.__thimblerig_round)
                    if self.__thimblerig_round is None:
                        return False

                time.sleep(2) # wait for animation
                self.__thimblerig_round = self.__thimblerig.select()
                if self.__thimblerig_round is None:
                    return False

            self._logFair.info(f"Thimblerig: {self.__thimblerig.get_points()}/300 balloons.")
        else:
            self._logFair.error("No tickets for playing!")
        return True

    def __pay_ticket_thimblerig(self) -> bool:
        if self.__thimblerig_round == 0:
            content = self.__http.pay_ticket("thimblerig")
            if content is None:
                return False
            self.__set_data(content)
        return True

    def play_wetgnome(self) -> bool:
        self._logFair.info(f"Reached: {self.__wetgnome.get_points()}/300 airsnakes.")
        while self.__tickets > 0:
            if self.__wetgnome_points >= REWARD_MAX:
                self._logFair.info("Wetgnome already finished!")
                return True

            if not self.__data["wetgnome"]["data"].get("wait", 0):
                if not self.__pay_ticket_wetgnome():
                    return False

            while 1 <= self.__wetgnome_round <= self.__wetgnome_maxrounds:
                if not self.__data["wetgnome"]["data"].get("wait", 0):
                    self.__wetgnome_round, game_id = self.__wetgnome.start(self.__wetgnome_round)
                    if self.__wetgnome_round is None:
                        return False

                time.sleep(2) # wait for animation
                self.__wetgnome_round = self.__wetgnome.select(game_id)
                if self.__wetgnome_round is None:
                    return False

            self._logFair.info(f"Reached: {self.__wetgnome.get_points()}/300 airsnakes.")
        else:
            self._logFair.error("No tickets for playing!")
        return True

    def __pay_ticket_wetgnome(self) -> bool:
        if self.__wetgnome_round == 0:
            content = self.__http.pay_ticket("wetgnome")
            if content is None:
                return False
            self.__set_data(content)
        return True