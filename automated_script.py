#!/usr/bin/env python
# -*- coding: utf-8 -*-

import src.Logger as logger
from src.WurzelBot import WurzelBot
import time, i18n, argparse


parser = argparse.ArgumentParser()
parser.add_argument('server', type=int, help='server number')
parser.add_argument('user', type=str, help='username for login')
parser.add_argument('password', type=str, help='password for login', default=False)
parser.add_argument("-l", '--log', help="If -l or --log Argument is passed, logging will be enabled.", action='store_true', default=False, required=False, dest="log")
parser.add_argument('lang', type=str, nargs='?', default=None, const='en')
args = parser.parse_args()

i18n.load_path.append('lang')
i18n.set('locale', args.lang)
i18n.set('fallback', 'en')

if args.log:
    logger.logger()

# Init connection
wurzelBot = WurzelBot()
wurzelBot.launchBot(args.server, args.user, args.password)


# Remove weed
print(i18n.t('wimpb.remove_weed_from_all_gardens'))
wurzelBot.removeWeedInAllGardens()

# Havest
wurzelBot.harvestAllGarden()

# Plant plants
planted = -1
plantedSingle = -1
while wurzelBot.hasEmptyFields() and planted != 0 and plantedSingle != 0:
    lowest = wurzelBot.getLowestPlantStockEntry()
    if lowest == 'Your stock is empty': break
    print(lowest + (i18n.t('wimpb.planting')))
    planted = wurzelBot.growPlantsInGardens(lowest)
    # If no more "lowest plants" can be grown, try to grow single field plants
    if planted == 0:
        lowestSingle = wurzelBot.getLowestSinglePlantStockEntry()
        if lowestSingle == 'Your stock is empty': break
        print(lowestSingle + (i18n.t('wimpb.planting')))
        plantedSingle = wurzelBot.growPlantsInGardens(lowestSingle)

# Water plants
time.sleep(3)
print(i18n.t('wimpb.watering_all_plants'))
wurzelBot.waterPlantsInAllGardens()

# Close connection
wurzelBot.exitBot()
