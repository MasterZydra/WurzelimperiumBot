#!/usr/bin/env python
# -*- coding: utf-8 -*-

import src.Logger as logger
from src.WurzelBot import WurzelBot

"""
Beispieldatei zur Verwendung des Bots.
Alle Stellen die angepasst werden müssen sind mit TODO gekennzeichnet.
"""

#TODO: Login Daten eintragen
user = ''
pw = ''
server = 1
portalacc = True

#Login und Initialisierung des Bots
wurzelBot = WurzelBot()
wurzelBot.launchBot(server, user, pw, portalacc)

#TODO: Aktionen definieren
#Beispiel: Alles ernten, in allen Gärten Kürbis anbauen und alles gießen
wurzelBot.harvestAllGarden()
wurzelBot.growPlantsInGardens('Salat', 2) # Nur 2 Pflanzen
wurzelBot.growPlantsInGardens('Kürbis') # So viele Pflanzen wie möglich
wurzelBot.growPlantsInAquaGardens('Sumpfdotterblume') # So viele Pflanzen wie möglich (außen)
wurzelBot.growPlantsInAquaGardens('Krebsschere') # So viele Pflanzen wie möglich (innen)
wurzelBot.waterPlantsInAllGardens()
wurzelBot.doSendBienen() # sendet die Bienen für 2h wenn möglich
wurzelBot.doCityQuest() # probiert die Stadtquest abzuschicken
#Deinitialisierung des Bots
wurzelBot.exitBot()




