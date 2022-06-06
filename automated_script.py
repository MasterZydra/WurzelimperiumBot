#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import src.Logger as logger
from src.WurzelBot import WurzelBot
import time


parser = argparse.ArgumentParser()
parser.add_argument('server', type=int, help='server number')
parser.add_argument('user', type=str, help='username for login')
parser.add_argument('password', type=str, help='password for login', default=False)
parser.add_argument("-l", '--log', help="If -l or --log Argument is passed, logging will be enabled.", action='store_true', default=False, required=False, dest="log")
args = parser.parse_args()

if args.log:
    logger.logger()

# Init connection
wurzelBot = WurzelBot()
wurzelBot.launchBot(args.server, args.user, args.password)


# Remove weed
print('Unkraut entfernen...')
wurzelBot.removeWeedInAllGardens()

# Havest
wurzelBot.harvestAllGarden()

# Plant plants
planted = -1
plantedSingle = -1
while wurzelBot.hasEmptyFields() and planted != 0 and plantedSingle != 0:
    lowest = wurzelBot.getLowestPlantStockEntry()
    lowestSingle = wurzelBot.getLowestSinglePlantStockEntry()
    if lowest == 'Your stock is empty': break
    print(lowest + ' anpflanzen...')
    print(lowestSingle + ' anpflanzen...')
    planted = wurzelBot.growPlantsInGardens(lowest)
    plantedSingle = wurzelBot.growPlantsInGardens(lowestSingle)

# Water plants
time.sleep(3)
print('Alle Pflanzen gießen...')
wurzelBot.waterPlantsInAllGardens()

# Close connection
wurzelBot.exitBot()
