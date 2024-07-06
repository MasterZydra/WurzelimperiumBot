#!/usr/bin/env python
# -*- coding: utf-8 -*-

import src.Logger as logger
from src.WurzelBot import WurzelBot
import i18n


"""
Beispieldatei zur Verwendung des Bots.
Alle Stellen die angepasst werden müssen sind mit TODO gekennzeichnet.
"""
#BG - Примерен файл за използване на бота
#BG - Всички места, които трябва да бъдат променени, са маркирани с TODO.

# Logging? Set to True to enable or False to disable logging.
#BG - Логиране? Задайте True за активиране или False за деактивиране на логирането.
log = True

#TODO: Login Daten eintragen
#BG - Въведете данните за вход
user = ''
pw = ''
server = 46
lang = 'de' # Define Region of Game and Language of bot (en/de/ru etc) #BG - Определете региона на играта и езика на бота (en/de/ru/bg etc)
portalacc = False

#Minimum WT to keep:
#BG - Минимален WT за задържане:
MINwt = 1000000

i18n.load_path.append('lang')
i18n.set('locale', lang)
i18n.set('fallback', 'en')

# Init logger
#BG - Инициализирайте логера
if log:
    logger.logger()

#Login und Initialisierung des Bots
#BG - Вход и инициализация на бота
wurzelBot = WurzelBot()
wurzelBot.launchBot(server, user, pw, lang, portalacc)

#TODO: Aktionen definieren
#BG -  Дефинирайте действия
#Beispiel: Alles ernten, in allen Gärten Kürbis anbauen und alles gießen
#BG - Пример: Прибиране на реколтата от всички градини, засаждане на тикви във всички градини и поливане на всичко.
wurzelBot.harvestAllGarden()
wurzelBot.growVegetablesInGardens('Salat', 2) # Nur 2 Pflanzen #BG- Само 2 растения
wurzelBot.growVegetablesInGardens('Kürbis') # So viele Pflanzen wie möglich #BG-Колкото се може повече растения
wurzelBot.growPlantsInAquaGardens('Wasserfeder') # So viele Pflanzen wie möglich (außen) #BG-Колкото се може повече растения (външни)
wurzelBot.growPlantsInAquaGardens('Schwertlilie') # So viele Pflanzen wie möglich (innen) #BG-Колкото се може повече растения (вътрешни)
wurzelBot.waterPlantsInAllGardens()
wurzelBot.get_daily_bonuses()
wurzelBot.sellWimpsProducts(0, 0) # Process Wimp Customers in Gardens #BG-Обработка на Wimp клиенти в градините


print(f'Kaufe Salat - im Lager sind: {wurzelBot.stock.get_stock_by_product_id("2")}')
wurzelBot.doBuyFromShop('Salat', 1) #buy plant with name and amount #BG-Купете растение по име и количество
wurzelBot.doBuyFromShop(2, 1) #buy plant with id and amount #BG-Купете растение по ID и количество
wurzelBot.stock.update()
print(f'neuer Lagerstand: {wurzelBot.stock.get_stock_by_product_id("2")}')

wurzelBot.sendBienen() #probiert die bienen für 2h zu senden - weitere ideen: zeit mitgabe, prüfen ob es gesendet wurde #BG-Опитва се да изпрати пчелите за 2 часа - други идеи: задаване на време, проверка дали е изпратено
wurzelBot.doCutBonsai() #probiert die äste zu schneiden - weitere ideen: prüfen ob es gesendet wurde #BG-Опитва се да отреже клоните - други идеи: проверка дали е изпратено
wurzelBot.infinityQuest() #probiert die infinityquest zulösen und kauft die fehlenden Produkte nach - weitere ideen: wt check #BG-Опитва се да реши Infinity Quest и купува липсващите продукти - други идеи: проверка на WT

#Deinitialisierung des Bots #BG-Деинициализация на бота
wurzelBot.exitBot()
