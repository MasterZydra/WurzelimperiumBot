#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.User import User
from src.bonsai.Http import Http
from src.bonsai.ShopProduct import *
from src.logger.Logger import Logger

class Bonsai:
    """Wrapper for the bonsaigarden"""
    #BG - Интерфейс за бонсаевата градина 

    def __init__(self):
        self.__http = Http()
        self.__initialiseBonsaiInfo(self.__http.init())

    def __initialiseBonsaiInfo(self, jContent) -> bool:
        """initialise info from JSON content of the bonsaigarden"""
        #BG - Инициализиране на информация от JSON съдържанието на бонсаевата градина
        if jContent is None:
            return False

        self.__jContentData = jContent['data']
        self.__bonsaiquestnr = jContent['questnr']
        self.__bonsaiquest = self.__getBonsaiQuest(jContent)
        self.__bonsaiavailable = self.__getAvailableBonsaiSlots(jContent)
        self.__slotinfos = self.__getBonsaiSlotInfos(jContent)
        return True

    def setBonsaiFarmData(self, jContent):
        """function to update the bonsaigarden data"""
        #BG - Функция за актуализиране на данните за бонсаевата градина
        self.__jContentData = jContent['data']
        self.__slotinfos = self.__getBonsaiSlotInfos(jContent)

    def get_level(self) -> int:
        return self.__jContentData['data']['level']

    def get_available_trees(self) -> list:
        level = self.get_level()
        trees = [MAIDENHAIR_PINE]  # Always available
        trees.extend(tree for lvl, tree in TREE_LEVELS if level >= lvl)
        return trees
    
    def get_available_scissor_packs(self, money_to_spend : int = None) -> list:
        if money_to_spend is None:
            money_to_spend = User().get_bar()

        packs = []
        packs.extend(pack for pack, _, price in SCISSOR_PACKS if money_to_spend >= price)
        return packs

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

    def buy_scissors(self, money_to_spend : int = None, pack = None) -> bool:
        """buys scissors from the shop"""
        if pack is None:
            packs = self.get_available_scissor_packs(money_to_spend)

            if len(packs) == 0:
                Logger().print('Not enough money to buy scissors')
                return False

            pack = packs[-1]

        amount = SCISSOR_PACKS[pack-1][1]
        price = SCISSOR_PACKS[pack-1][2]
        Logger().print(f'Rebuying {amount} normal scissors for {price} wT.')

        jContent = self.__http.buyAndPlaceBonsaiItem(NORMAL_SCISSOR, pack, 0)
        if jContent is None:
            return False
        self.setBonsaiFarmData(jContent)
        return True

    def cutAllBonsai(self, min_scissor_stock=50, money_to_spend : int = None) -> bool:
        """cuts every branch of available bonsai and rebuys scissors if necessary"""
	#BG - Отрязва всички клони на наличните бонсаи и купува нови ножици, ако е необходимо.
        sissorID = None
        sissorLoads = None
        for key, value in self.__jContentData['items'].items():
            if value['item'] == str(NORMAL_SCISSOR):
                sissorID = key
                sissorLoads = value['loads']
                Logger().info(f"In storage: {sissorLoads} normal scissors with ID {sissorID}")

        if sissorID is None or int(sissorLoads) < min_scissor_stock:
            self.buy_scissors(money_to_spend)

        for key in self.__slotinfos.keys():
            Logger().info(f'Bonsai in slot {key}:')

            if self.__slotinfos[key][2] is None:
                # No tree in slot
                continue

            for branch in self.__slotinfos[key][2]:
                jContent = self.__http.cutBranch(key, sissorID, branch)
                if jContent is None:
                    return False
                self.setBonsaiFarmData(jContent)
                Logger().print(f'Cut branch {branch}')

        return True

    def checkBonsai(self, finish_level=2, bonsai=None) -> bool:
        """Checks if bonsai is a given level: finishes bonsai to bonsaigarden, renews it with highest available bonsai and a normal pot"""
        if bonsai is None:
            bonsai = self.get_available_trees()[-1]

        for key in self.__slotinfos.keys():
            level = self.__slotinfos[key][0]
            if level is None or level >= finish_level:
                Logger().print(f'Finish Bonsai in slot {key} with level {level}')

                if level is not None:
                    if self.__http.finishBonsai(key) is None:
                        return False

                if self.__http.buyAndPlaceBonsaiItem(SIMPLE_POT, 1, key) is None:
                    return False

                jContent = self.__http.buyAndPlaceBonsaiItem(bonsai, 1, key)
                if jContent is None:
                    return False

                self.setBonsaiFarmData(jContent)
            else:
                Logger().print(f'Do nothing: Bonsai in slot {key} is level {level}')

        return True
