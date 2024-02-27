#!/usr/bin/env python
# -*- coding: utf-8 -

from collections import Counter
from src.core.HTTPCommunication import HTTPConnection
from src.Quests_lists import *
from src.Spieler import Spieler

class Quest:
    def __init__(self, httpConnection: HTTPConnection, spieler: Spieler):
        self.__httpConn = httpConnection
        self.__spieler = spieler

    def getQuestProducts(self, quest_name, quest_number=0):
        if quest_name == "BigQuest":
            quest_products = self.__getBigQuestProducts()
        elif quest_name == "MainQuest":
            quest_products = self.__getMainQuestProducts(quest_number)
        elif quest_name == "CactusQuest":
            quest_products = self.__getCactusQuestProducts()

        return quest_products

    def __getBigQuestProducts(self):
        """
        Returns a dictionary of monthly big quest products with amount of products
        """
        #BG-Връща речник с месечните продукти за Голямата мисия, заедно с техните количества.
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
        #BG-Връща речник с продуктите от мисиите от главния клон и техните количества @param quest_number: номер на мисията, за която да се върнат данните; ако е 0, връща данните за текущата мисия @return: речник с продукти и количества


        if quest_number == 0:
            quest_number = self.__httpConn.getInfoFromStats("CompletedQuests") + 1

        raw_products = main_quest.get(str(quest_number), {})
        products = {str(k): v for k, v in raw_products.items()}
        return products

    def __getCactusQuestProducts(self):
        quest_products = []

        def add_quest_products(quest_name, level_requirement):
            if int(self.__spieler.getLevelNr()) >= level_requirement:
                quest_number = self.__httpConn.getInfoFromStats(quest_name) + 1
                raw_products = quest_data.get(str(quest_number), {})
                if raw_products:
                    products = {str(k): v for k, v in raw_products.items()}
                    quest_products.append(products)

        quest_data = cactus_quest
        add_quest_products("CactusQuest", 12)
        add_quest_products("EchinoQuest", 12)
        add_quest_products("BigheadQuest", 15)
        add_quest_products("OpuntiaQuest", 18)
        add_quest_products("SaguaroQuest", 21)

        return quest_products
