#!/usr/bin/env python
# -*- coding: utf-8 -*-

import src.Logger as logger
from src.WurzelBot import WurzelBot
import i18n


"""
Beispieldatei zur Verwendung des Bots.
Alle Stellen die angepasst werden müssen sind mit TODO gekennzeichnet.
"""

# Logging? Set to True to enable or False to disable logging.
log = True

#TODO: Login Daten eintragen
user = ''
pw = ''
server = 46
lang = 'de' # Define Region of Game and Language of bot (en/de/ru etc)
portalacc = False

i18n.load_path.append('lang')
i18n.set('locale', lang)
i18n.set('fallback', 'en')

# Init logger
if log:
    logger.logger()

#Login und Initialisierung des Bots
wurzelBot = WurzelBot()
wurzelBot.launchBot(server, user, pw, lang, portalacc)

#TODO: Aktionen definieren
#Beispiel: Alles ernten, in allen Gärten Kürbis anbauen und alles gießen
wurzelBot.harvestAllGarden()
wurzelBot.growPlantsInGardens('Salat', 2) # Nur 2 Pflanzen
wurzelBot.growPlantsInGardens('Kürbis') # So viele Pflanzen wie möglich
wurzelBot.growPlantsInAquaGardens('Wasserfeder') # So viele Pflanzen wie möglich (außen)
wurzelBot.growPlantsInAquaGardens('Schwertlilie') # So viele Pflanzen wie möglich (innen)
wurzelBot.waterPlantsInAllGardens()
wurzelBot.getDailyLoginBonus()
wurzelBot.sellWimpsProducts(0, 0) # Process Wimp Customers in Gardens


print(f'Kaufe Salat - im Lager sind: {wurzelBot.storage.getStockByProductID("2")}')
wurzelBot.doBuyFromShop('Salat', 1) #buy plant with name and amount
wurzelBot.doBuyFromShop(2, 1) #buy plant with id and amount
wurzelBot.storage.updateNumberInStock()
print(f'neuer Lagerstand: {wurzelBot.storage.getStockByProductID("2")}')

wurzelBot.doSendBienen() #probiert die bienen für 2h zu senden - weitere ideen: zeit mitgabe, prüfen ob es gesendet wurde
wurzelBot.doCutBonsai() #probiert die äste zu schneiden - weitere ideen: prüfen ob es gesendet wurde
wurzelBot.infinityQuest() #probiert die infinityquest zulösen und kauft die fehlenden Produkte nach - weitere ideen: wt check

#Deinitialisierung des Bots
wurzelBot.exitBot()
