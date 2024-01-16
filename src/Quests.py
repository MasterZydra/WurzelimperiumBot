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
        if int(self.__spieler.getLevelNr()) >= 12:
            # Initial Cactus quest
            #BG- Главна Кактус мисии
            quest_number = self.__httpConn.getInfoFromStats("CactusQuest")
            raw_products = cactus_quest.get(str(quest_number), {})
            if len(raw_products) > 0:
                products = {str(k): v for k, v in raw_products.items()}
                quest_products.append(products)
            # Echino quests
            #BG- Таралежова мисия
            quest_number = self.__httpConn.getInfoFromStats("EchinoQuest") + 1
            raw_products = echinocactus_quest.get(str(quest_number), {})
            if len(raw_products) > 0:
                products = {str(k): v for k, v in raw_products.items()}
                quest_products.append(products)
            # Bighead quests
            #BG- Голяма глава мисия
            if int(self.__spieler.getLevelNr()) >= 15:
                quest_number = self.__httpConn.getInfoFromStats("BigheadQuest") + 1
                raw_products = bighead_quest.get(str(quest_number), {})
                if len(raw_products) > 0:
                    products = {str(k): v for k, v in raw_products.items()}
                    quest_products.append(products)
            # Opuntia quests
            #BG- Опунтия мисия
            if int(self.__spieler.getLevelNr()) >= 18:
                quest_number = self.__httpConn.getInfoFromStats("OpuntiaQuest") + 1
                raw_products = opuntia_quest.get(str(quest_number), {})
                if len(raw_products) > 0:
                    products = {str(k): v for k, v in raw_products.items()}
                    quest_products.append(products)
            # Saguaro quests
            #BG- Сагуаро мисия
            if int(self.__spieler.getLevelNr()) >= 21:
                quest_number = self.__httpConn.getInfoFromStats("SaguaroQuest") + 1
                raw_products = saguaro_quest.get(str(quest_number), {})
                if len(raw_products) > 0:
                    products = {str(k): v for k, v in raw_products.items()}
                    quest_products.append(products)

        return quest_products
