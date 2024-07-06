#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from src.core.HTTPCommunication import HTTPConnection

class Bonsai():
    """Wrapper for the bonsaigarden"""
    #BG - Интерфейс за бонсаевата градина 

    def __init__(self, httpConnection: HTTPConnection):
        self._httpConn = httpConnection
        self._logBonsai = logging.getLogger('bot.Bonsai')
        self._logBonsai.setLevel(logging.DEBUG)
        self.__initialiseBonsaiInfo(self._httpConn.bonsaiInit())

    def __initialiseBonsaiInfo(self, jContent):
        """initialise info from JSON content of the bonsaigarden"""
	#BG - Инициализиране на информация от JSON съдържанието на бонсаевата градина
        self.__jContentData = jContent['data']
        self.__bonsaiquestnr = jContent['questnr']
        self.__bonsaiquest = self.__getBonsaiQuest(jContent)
        self.__bonsaiavailable = self.__getAvailableBonsaiSlots(jContent)
        self.__slotinfos = self.__getBonsaiSlotInfos(jContent)

    def setBonsaiFarmData(self, jContent):
        """function to update the bonsaigarden data"""
        #BG - Функция за актуализиране на данните за бонсаевата градина
        self.__jContentData = jContent['data']
        self.__slotinfos = self.__getBonsaiSlotInfos(jContent)

    def __getBonsaiQuest(self, jContent):
        """searches for available bonsai quest in the JSON content and returns the questdata"""
	#BG - Търси налични куестове за бонсай в JSON съдържанието и връща данните за куеста.
        bonsaiQuest = {}
        i = 1
        for course in jContent['questData']['products']:
            new = {i: {'pid': course['pid'], 'type': course['name']}}
            bonsaiQuest.update(new)
            i = i + 1
        return bonsaiQuest

    def __getAvailableBonsaiSlots(self, jContent): #TODO: usecase of this?
        """searches for available bonsai in the JSON Content and returns them"""
	#BG - Търси налични бонсаи в JSON съдържанието и ги връща. - Каква е употребата?
        availableTreeSlots = []

        for tree in jContent['data']['data']['slots']:
            if "block" not in jContent['data']['data']['slots'][tree]:
                availableTreeSlots.append(int(tree))

        # sorting via an empty array changes object type to None
        if len(availableTreeSlots) > 0:
            availableTreeSlots.sort(reverse=False)

        return availableTreeSlots

    def __getBonsaiSlotInfos(self, jContent):
        """searches for breeded bonsai in the JSON content and returns level, reward and branches"""
	#BG - Търси размножени бонсаи в JSON съдържанието и връща ниво, награда и разклонения.
        availableBonsais = {}

        for bonsai in jContent['data']['breed']:
            bonsaiLevel: int = jContent['data']['breed'][bonsai]['level']
            bonsaiReward: dict = jContent['data']['breed'][bonsai]['reward']
            bonsaiSlotNr = jContent['data']['breed'][bonsai]['slot']
            bonsaiBranches = jContent['data']['breed'][bonsai]['branches']
            availableBonsais[bonsaiSlotNr] = [bonsaiLevel, bonsaiReward, bonsaiBranches]

        return availableBonsais

    def cutAllBonsai(self, min_scissor_stock=50) -> None:
        """cuts every branch of available bonsai and rebuys scissors if necessary"""
	#BG - Отрязва всички клони на наличните бонсаи и купува нови ножици, ако е необходимо.
        sissorID = None
        sissorLoads = None
        for key, value in self.__jContentData['items'].items():
            if value['item'] == "21":
                sissorID = key
                sissorLoads = value['loads']
                self._logBonsai.info(f"In storage: {sissorLoads} normal scissors with ID {sissorID}")
        if sissorID is None or int(sissorLoads) < min_scissor_stock:
            self._logBonsai.info("Rebuying 500 normal scissors for 80.000 wT.")
            jContent = self._httpConn.buyAndPlaceBonsaiItem(21, 4, 0)
            self.setBonsaiFarmData(jContent)

        for key in self.__slotinfos.keys():
            self._logBonsai.info(f'Bonsai in slot {key}:')
            for branch in self.__slotinfos[key][2]:
                jContent = self._httpConn.cutBonsaiBranch(key, sissorID, branch)
                self.setBonsaiFarmData(jContent)
                self._logBonsai.info(f'Cut branch {branch}')


    def checkBonsai(self, finish_level=2) -> None:
        """checks if bonsai is a certain level: finishes bonsai to bonsaigarden and renews it with a Zypresse and a normal pot"""
	#BG - Проверява дали бонсаят е с определено ниво: допълва бонсая към градината и го подновява с кипарис и стандартна саксия.
        for key in self.__slotinfos.keys():
            level = self.__slotinfos[key][0]
            if level >= finish_level:
                self._logBonsai.info(f'Finish Bonsai in slot {key} with level {level}')
                jContent = self._httpConn.finishBonsai(key)
                jContent = self._httpConn.buyAndPlaceBonsaiItem(11, 1, key)
                jContent = self._httpConn.buyAndPlaceBonsaiItem(5, 1, key)
                self.setBonsaiFarmData(jContent)
            else:
                self._logBonsai.info(f'Do nothing: Bonsai in slot {key} is level {level}')
