#!/usr/bin/env python
# -*- coding: utf-8 -

from collections import Counter

class Quest:

    def __init__(self, httpConnection):
        self.__httpConn = httpConnection

    def __getBigQuestProducts(self):
        quest_data = self.__httpConn.getBigQuestData()
        current_quest = quest_data['current']
        quest_products = quest_data['data']['quests'][str(current_quest)]['need']
        have_products = quest_data['data']['quests'][str(current_quest)].get('have', {})
        quest_products = dict(Counter(quest_products) - Counter(have_products))

        return quest_products

    def getQuestProducts(self, quest_name):
        if quest_name == "BigQuest":
            quest_products = self.__getBigQuestProducts()

        return quest_products
