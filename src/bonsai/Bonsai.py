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
        self.__init_info(self.__http.init())

    def __init_info(self, content) -> bool:
        """initialise info from JSON content of the bonsaigarden"""
        #BG - Инициализиране на информация от JSON съдържанието на бонсаевата градина
        if content is None:
            return False

        self.__data = content['data']
        self.__quest_nr = content['questnr']
        self.__quest = self.__get_quest(content)
        self.__bonsaiavailable = self.__get_available_bonsai_slots(content)
        self.__slot_infos = self.__get_slot_infos(content)
        return True

    def __set_data(self, content):
        """function to update the bonsaigarden data"""
        #BG - Функция за актуализиране на данните за бонсаевата градина
        self.__data = content['data']
        self.__slot_infos = self.__get_slot_infos(content)

    def get_level(self) -> int:
        return self.__data['data']['level']

    def get_available_trees(self) -> list:
        level = self.get_level()
        trees = [MAIDENHAIR_PINE]  # Always available
        trees.extend(tree for lvl, tree in TREE_LEVELS if level >= lvl)
        return trees

    def get_best_tree(self, allowed_prices: list = ['money', 'coins']) -> int:
        trees = self.get_available_trees()
        best_tree = None
        for tree in trees:
            # Get price of tree
            price = get_tree_price(tree)
            if price is None:
                continue
            price, unit = price

            # Check if the unit of price is allowed
            if unit not in allowed_prices:
                continue

            # Check is user has enough money, fruits or coins to pay for item
            if (unit == 'money' and User().get_bar() >= price) or \
                (unit == 'coins' and User().get_coins() >= price):
                best_tree = tree

        return best_tree

    def get_available_scissor_packs(self, money_to_spend : int = None) -> list:
        if money_to_spend is None:
            money_to_spend = User().get_bar()

        packs = []
        packs.extend(pack for pack, _, price in SCISSOR_PACKS if money_to_spend >= price)
        return packs

    def __get_quest(self, content):
        """searches for available bonsai quest in the JSON content and returns the questdata"""
	#BG - Търси налични куестове за бонсай в JSON съдържанието и връща данните за куеста.
        bonsaiQuest = {}
        i = 1
        for course in content['questData']['products']:
            new = {i: {'pid': course['pid'], 'type': course['name']}}
            bonsaiQuest.update(new)
            i = i + 1
        return bonsaiQuest

    def __get_available_bonsai_slots(self, content): #TODO: usecase of this?
        """searches for available bonsai in the JSON Content and returns them"""
	#BG - Търси налични бонсаи в JSON съдържанието и ги връща. - Каква е употребата?
        available_slots = []

        for tree in content['data']['data']['slots']:
            if "block" not in content['data']['data']['slots'][tree]:
                available_slots.append(int(tree))

        # sorting via an empty array changes object type to None
        if len(available_slots) > 0:
            available_slots.sort(reverse=False)

        return available_slots

    def __get_slot_infos(self, content):
        """searches for breeded bonsai in the JSON content and returns level, reward and branches"""
	#BG - Търси размножени бонсаи в JSON съдържанието и връща ниво, награда и разклонения.
        available_bonsais = {}

        for bonsai in content['data']['breed']:
            level: int = content['data']['breed'][bonsai]['level']
            reward: dict = content['data']['breed'][bonsai]['reward']
            slot_no = content['data']['breed'][bonsai]['slot']
            branches = content['data']['breed'][bonsai]['branches']
            bowl = content['data']['breed'][bonsai]['bowl']
            available_bonsais[slot_no] = [level, reward, branches, bowl]

        return available_bonsais

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

        content = self.__http.buy_and_place(NORMAL_SCISSOR, pack, 0)
        if content is None:
            return False
        self.__set_data(content)
        return True

    def cut_all(self, min_scissor_stock=50, money_to_spend : int = None) -> bool:
        """cuts every branch of available bonsai and rebuys scissors if necessary"""
	#BG - Отрязва всички клони на наличните бонсаи и купува нови ножици, ако е необходимо.
        sissorID = None
        sissorLoads = None
        for key, value in self.__data['items'].items():
            if value['item'] == str(NORMAL_SCISSOR):
                sissorID = key
                sissorLoads = value['loads']
                Logger().debug(f"In storage: {sissorLoads} normal scissors with ID {sissorID}")

        if sissorID is None or int(sissorLoads) < min_scissor_stock:
            self.buy_scissors(money_to_spend)

        for key in self.__slot_infos.keys():
            Logger().debug(f'Bonsai in slot {key}:')

            if self.__slot_infos[key][2] is None:
                # No tree in slot
                continue

            for branch in self.__slot_infos[key][2]:
                content = self.__http.cut(key, sissorID, branch)
                if content is None:
                    return False
                self.__set_data(content)
                Logger().print(f'Cut branch {branch}')

        return True

    def check(self, finish_level: int = 2, bonsai = None, allowed_prices: list = ['money', 'coins']) -> bool:
        """
        Checks if bonsai is a given level: finishes bonsai to bonsaigarden, renews it with highest available bonsai and a normal pot
        """
        if bonsai is None:
            bonsai = self.get_best_tree(allowed_prices)
            if bonsai is None:
                Logger().print('No bonsai available or affordable')
                return False

        # Add unused slot to slot_infos so that it can be used to place a bonsai
        for slot in self.__bonsaiavailable:
            if str(slot) not in self.__slot_infos:
                self.__slot_infos[str(slot)] = [None, None, None, None]

        for key in self.__slot_infos.keys():
            level = self.__slot_infos[key][0]
            if level is None or level >= finish_level:
                if level is not None:
                    Logger().print(f'Finish Bonsai in slot {key} with level {level}')
                else:
                    Logger().print(f'Place Bonsai in slot {key}')

                if level is not None:
                    if self.__http.finish(key) is None:
                        return False

                if self.__slot_infos[key][3] is None or self.__slot_infos[key][3] == '0':
                    # TODO use pot/bowl from stock if possible
                    if self.__http.buy_and_place(SIMPLE_POT, 1, key) is None:
                        return False

                content = self.__http.buy_and_place(bonsai, 1, key)
                if content is None:
                    return False

                self.__set_data(content)

                if not User().update():
                    return False
            else:
                Logger().debug(f'Do nothing: Bonsai in slot {key} is level {level}')

        return True
