#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import src.Main as main
import time


parser = argparse.ArgumentParser()
parser.add_argument('server', type=int, help='server number')
parser.add_argument('user', type=str, help='username for login')
parser.add_argument('password', type=str, help='password for login', default=False)
parser.add_argument("-l", '--log', help="If -l or --log Argument is passed, logging will be enabled.", action='store_true', default=False, required=False, dest="log")
args = parser.parse_args()

if args.log:
    main.logger()

# Init connection
wurzelBot = main.initWurzelBot()
wurzelBot.launchBot(args.server, args.user, args.password)


# Remove weed
print('Unkraut entfernen...')
wurzelBot.removeWeedInAllGardens()

# Havest
wurzelBot.harvestAllGarden()

# Plant plants
planted = -1
while wurzelBot.hasEmptyFields() and planted != 0:
    lowest = wurzelBot.getLowestPlantStockEntry()
    if lowest == 'Your stock is empty': break
    print(lowest + ' anpflanzen...')
    planted = wurzelBot.growPlantsInGardens(lowest)

# Water plants
time.sleep(3)
print('Alle Pflanzen gießen...')
wurzelBot.waterPlantsInAllGardens()

# Close connection
wurzelBot.exitBot()
