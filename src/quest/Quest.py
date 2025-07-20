#!/usr/bin/env python
# -*- coding: utf-8 -

from src.quest.Http import Http
from src.quest.Missions import Missions
from src.core.User import User
from src.logger.Logger import Logger
from collections import Counter

class Quest:
    def __init__(self):
        self.__http = Http()

    def get_quest_products(self, quest_name, quest_number=0):
        """
        @param quest_name e.g. 'MainQuest', 'BigQuest', 'CactusQuest'
        @param quest_number: Only required for 'MainQuest'. Number of quest to return, if 0 - returns current quest
        """
        if quest_name == "MainQuest":
            return self.__get_main_quest_products(quest_number)
        if quest_name == "BigQuest":
            return self.__get_big_quest_products()
        if quest_name == "CactusQuest":
            return self.__get_cactus_quest_products()
        Logger().print_exception(f'Quest {quest_name} is not implemented')
        return None

    def __get_big_quest_products(self):
        """Returns a dictionary of monthly big quest products with amount of products"""
        quest_data = self.__http.get_big_quest_data()
        if quest_data is None:
            return None
        current_quest = quest_data['current']
        quest_products = quest_data['data']['quests'][str(current_quest)]['need']
        have_products = quest_data['data']['quests'][str(current_quest)].get('have', {})
        return dict(Counter(quest_products) - Counter(have_products))

    def __get_main_quest_products(self, quest_number=0) -> dict[str, int]:
        """
        Returns dictionary of Main branch quests products with amount
        @param quest_number: number of quest to return, if 0 - returns current quest
        @return: dict of products with amount
        """
        if quest_number == 0:
            quest_number = User().get_stats("CompletedQuests") + 1

        raw_products = Missions.main_quest().get(str(quest_number), {})
        return {str(k): v for k, v in raw_products.items()}

    def __get_cactus_quest_products(self):
        quest_products = []
        if User().get_level() >= 12:
            # Initial Cactus quest
            quest_number = User().get_stats("CactusQuest")
            if quest_number is None:
                return None
            raw_products = Missions.cactus_quest().get(str(quest_number), {})
            if len(raw_products) > 0:
                products = {str(k): v for k, v in raw_products.items()}
                quest_products.append(products)
                return quest_products

            # Echino quests
            quest_number = User().get_stats("EchinoQuest")
            if quest_number is None:
                return None
            raw_products = Missions.echinocactus_quest().get(str(quest_number + 1), {})
            if len(raw_products) > 0:
                products = {str(k): v for k, v in raw_products.items()}
                quest_products.append(products)
                return quest_products

            # Bighead quests
            if User().get_level() >= 15:
                quest_number = User().get_stats("BigheadQuest")
                if quest_number is None:
                    return None
                raw_products = Missions.bighead_quest().get(str(quest_number + 1), {})
                if len(raw_products) > 0:
                    products = {str(k): v for k, v in raw_products.items()}
                    quest_products.append(products)
                    return quest_products

            # Opuntia quests
            if User().get_level() >= 18:
                quest_number = User().get_stats("OpuntiaQuest")
                if quest_number is None:
                    return None
                raw_products = Missions.opuntia_quest().get(str(quest_number + 1), {})
                if len(raw_products) > 0:
                    products = {str(k): v for k, v in raw_products.items()}
                    quest_products.append(products)
                    return quest_products

            # Saguaro quests
            if User().get_level() >= 21:
                quest_number = User().get_stats("SaguaroQuest")
                if quest_number is None:
                    return None
                raw_products = Missions.saguaro_quest().get(str(quest_number + 1), {})
                if len(raw_products) > 0:
                    products = {str(k): v for k, v in raw_products.items()}
                    quest_products.append(products)
                    return quest_products

        return quest_products
