#!/usr/bin/env python
# -*- coding: utf-8 -*-

import src.Logger as logger
from src.WurzelBot import WurzelBot


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
# lang = de/en/ru
lang = 'de'

# Init logger
if log == True:
    logger.logger()

#Login und Initialisierung des Bots
wurzelBot = WurzelBot()
wurzelBot.launchBot(server, user, pw, lang)

#TODO: Aktionen definieren
#Beispiel: Alles ernten, in allen Gärten Kürbis anbauen und alles gießen
wurzelBot.harvestAllGarden()
wurzelBot.growPlantsInGardens('Salat', 2) # Nur 2 Pflanzen
wurzelBot.growPlantsInGardens('Kürbis') # So viele Pflanzen wie möglich
wurzelBot.waterPlantsInAllGardens()

#Deinitialisierung des Bots
wurzelBot.exitBot()




