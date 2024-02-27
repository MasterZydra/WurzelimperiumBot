#!/usr/bin/env python
# -*- coding: utf-8 -*-

import src.Logger as logger
from src.WurzelBot import WurzelBot
import time
import i18n
import argparse

def setup_argparse():
    # Set up argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument('server', type=int, help='server number')
    parser.add_argument('user', type=str, help='username for login')
    parser.add_argument('password', type=str, help='password for login', default=False)
    parser.add_argument('-p', '--portal', help="If -p or --portal Argument is passed, Portal Account Login will be used.", action='store_true', default=False, required=False, dest="portalacc")
    parser.add_argument('-l', '--log', help="If -l or --log Argument is passed, logging will be enabled.", action='store_true', default=False, required=False, dest="log")
    parser.add_argument('lang', help="Set Language and Region for the Game and Bot", type=str, nargs='?', default=None, const='en')
    return parser.parse_args()

def initialize_i18n(lang):
    # Initialize internationalization
    i18n.load_path.append('lang')
    i18n.set('locale', lang)
    i18n.set('fallback', 'en')

def initialize_logging(log_enabled):
    # Initialize logging if enabled
    if log_enabled:
        logger.logger()

def main():
    # Main function of the script
    args = setup_argparse()
    initialize_i18n(args.lang)
    initialize_logging(args.log)

    # Initialize and connect WurzelBot
    wurzelBot = WurzelBot()
    success = wurzelBot.launchBot(args.server, args.user, args.password, args.lang, args.portalacc)
    if not success:
        exit(-1)

    # Perform various actions
    remove_weed(wurzelBot)
    harvest_gardens(wurzelBot)
    plant_vegetables(wurzelBot)
    water_plants(wurzelBot)
    claim_daily_bonus(wurzelBot)
    process_wimps(wurzelBot)
    close_connection(wurzelBot)

def remove_weed(bot):
    # Remove weeds
    print(i18n.t('wimpb.remove_weed_from_all_gardens'))
    bot.removeWeedInAllGardens()

def harvest_gardens(bot):
    # Harvest gardens
    print(i18n.t('wimpb.harvest_all_gardens'))
    bot.harvestAllGarden()

def plant_vegetables(bot):
    # Plant vegetables
    while bot.hasEmptyFields():
        lowest = bot.getLowestVegetableStockEntry()
        if lowest == 'Your stock is empty':
            break
        print(i18n.t('wimpb.grow_plant_X', plant=lowest))
        if not bot.growVegetablesInGardens(lowest):
            break

        lowest_single = bot.getLowestSingleVegetableStockEntry()
        if lowest_single == 'Your stock is empty':
            break
        print(i18n.t('wimpb.grow_plant_X', plant=lowest_single))
        if not bot.growVegetablesInGardens(lowest_single):
            break

def water_plants(bot):
    # Water plants
    time.sleep(3)
    print(i18n.t('wimpb.watering_all_plants'))
    bot.waterPlantsInAllGardens()

def claim_daily_bonus(bot):
    # Claim daily bonus
    print(i18n.t('wimpb.claim_bonus'))
    bot.getDailyLoginBonus()

def process_wimps(bot):
    # Process wimps
    print(i18n.t('wimpb.process_wimps'))
    bot.sellWimpsProducts(0,0)

def close_connection(bot):
    # Close connection
    print(i18n.t('wimpb.close_connection'))
    bot.exitBot()

if __name__ == "__main__":
    main()
