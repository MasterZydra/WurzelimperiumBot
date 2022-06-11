#!/usr/bin/env python
# -*- coding: utf-8 -*-

import src.Main as main


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
wurzelBot = main.initWurzelBot()
wurzelBot.launchBot(server, user, pw, portalacc)

#TODO: Aktionen definieren
#Beispiel: Alles ernten, in allen Gärten Kürbis anbauen und alles gießen
wurzelBot.harvestAllGarden()
wurzelBot.growPlantsInGardens('Salat', 2) # Nur 2 Pflanzen
wurzelBot.growPlantsInGardens('Kürbis') # So viele Pflanzen wie möglich
wurzelBot.growPlantsInAquaGardens('Sumpfdotterblume')
wurzelBot.growPlantsInAquaGardens('Krebsschere')
wurzelBot.waterPlantsInAllGardens()
wurzelBot.doSendBienen()
wurzelBot.doCityQuest()
#Deinitialisierung des Bots
wurzelBot.exitBot()




