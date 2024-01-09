#!/usr/bin/env python
# -*- coding: utf-8 -*-

import src.Logger as logger
from src.WurzelBot import WurzelBot
import time, i18n, argparse


parser = argparse.ArgumentParser()
parser.add_argument('server', type=int, help='server number')
parser.add_argument('user', type=str, help='username for login')
parser.add_argument('password', type=str, help='password for login', default=False)
parser.add_argument('-p', '--portal', help="If -p or --portal Argument is passed, Portal Account Login will be used.", action='store_true', default=False, required=False, dest="portalacc")
parser.add_argument('-l', '--log', help="If -l or --log Argument is passed, logging will be enabled.", action='store_true', default=False, required=False, dest="log")
parser.add_argument('lang', help="Set Language and Region for the Game and Bot", type=str, nargs='?', default=None, const='en')
args = parser.parse_args()

i18n.load_path.append('lang')
i18n.set('locale', args.lang)
i18n.set('fallback', 'en')

if args.log:
    logger.logger()

# Init connection
#BG- Създаване на връзка
wurzelBot = WurzelBot()
succ = wurzelBot.launchBot(args.server, args.user, args.password, args.lang, args.portalacc)
if succ != True:
    exit(-1)

# Remove weed
#BG-Премахване на плевели
print(i18n.t('wimpb.remove_weed_from_all_gardens'))
wurzelBot.removeWeedInAllGardens()

# Harvest
#BG-Жътва
wurzelBot.harvestAllGarden()

# Plant plants
#BG-Посаждане на растения
planted = -1
plantedSingle = -1
while wurzelBot.hasEmptyFields() and planted != 0 and plantedSingle != 0:
    lowest = wurzelBot.getLowestVegetableStockEntry()
    if lowest == 'Your stock is empty': break
    print(i18n.t('wimpb.grow_plant_X', plant=lowest))
    planted = wurzelBot.growVegetablesInGardens(lowest)
    # If no more "lowest plants" can be grown, try to grow single field plants
    #BG-Ако няма растения с малък брой, посаждане на еденични такива.
    if planted == 0:
        lowestSingle = wurzelBot.getLowestSingleVegetableStockEntry()
        if lowestSingle == 'Your stock is empty': break
        print(i18n.t('wimpb.grow_plant_X', plant=lowestSingle))
        plantedSingle = wurzelBot.growVegetablesInGardens(lowestSingle)

# Water plants
#BG-Поливане на растенията
time.sleep(3)
print(i18n.t('wimpb.watering_all_plants'))
wurzelBot.waterPlantsInAllGardens()
# Claim Daily
#BG-Събиране на дневният бонус
print(i18n.t('wimpb.claim_bonus'))
wurzelBot.getDailyLoginBonus()
# Process Wimp Customers in Gardens
#BG-Изпълни нуждите на Wimps в градините
print(i18n.t('wimpb.process_wimps'))
wurzelBot.sellWimpsProducts(0,0)

# Close connection
#BG-Затваряне на връзката
wurzelBot.exitBot()
