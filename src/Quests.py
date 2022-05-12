#!/usr/bin/env python
# -*- coding: utf-8 -

from collections import Counter
from src.Quests_lists import *

class Quest:

    def __init__(self, httpConnection):
        self.__httpConn = httpConnection

    def getQuestProducts(self, quest_name, quest_number=0):
        if quest_name == "BigQuest":
            quest_products = self.__getBigQuestProducts()
        elif quest_name == "MainQuest":
            quest_products = self.__getMainQuestProducts(quest_number)

        return quest_products

    def __getBigQuestProducts(self):
        """
        Returns a dictionary of monthly big quest products with amount of products
        """
        quest_data = self.__httpConn.getBigQuestData()
        current_quest = quest_data['current']
        quest_products = quest_data['data']['quests'][str(current_quest)]['need']
        have_products = quest_data['data']['quests'][str(current_quest)].get('have', {})
        quest_products = dict(Counter(quest_products) - Counter(have_products))

        return quest_products

    def __getMainQuestProducts(self, quest_number=0):
        """
        Returns dictionary of Main branch quests products with amount
        @param quest_number: number of quest to return, if 0 - returns current quest
        @return: dict of products with amount
        """
        if quest_number == 0:
            quest_number = self.__httpConn.getInfoFromStats("CompletedQuests") + 1

        products = main_quest.get(str(quest_number), {})
        return products
