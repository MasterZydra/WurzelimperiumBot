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

#Login und Initialisierung des Bots
wurzelBot = main.initWurzelBot()
wurzelBot.launchBot(46, user, pw)

#TODO: Aktionen definieren
#Beispiel: Alles ernten, in allen Gärten Kürbis anbauen und alles gießen
wurzelBot.harvestAllGarden()
wurzelBot.growPlantsInGardens('Kürbis')
wurzelBot.waterPlantsInAllGardens()

#Deinitialisierung des Bots
wurzelBot.exitBot()




