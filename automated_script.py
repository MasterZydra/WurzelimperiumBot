#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import time
import i18n
from src.core.Config import Config
from src.logger.Logger import Logger
from src.WurzelBot import WurzelBot

def main():
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
        Config().log_to_stdout = True

    # Init connection
    # BG- Създаване на връзка
    wurzelBot = WurzelBot()
    succ = wurzelBot.login(args.server, args.user, args.password, args.lang, args.portalacc)
    if not succ:
        exit(-1)

    try:
        # Check if the bot should be stopped
        # BG-Проверка дали бота трябва да бъде спрян
        if wurzelBot.get_stop_bot_note():
            Logger().print(i18n.t('wimpb.stop_wbot'))
            wurzelBot.logout()
            return

        # Remove weed
        # BG-Премахване на плевели
        Logger().print('')
        Logger().print(i18n.t('wimpb.remove_weed_from_all_gardens'))
        wurzelBot.remove_weeds()

        # Harvest
        # BG-Жътва
        Logger().print('')
        wurzelBot.harvest()

        # Plant plants
        # BG-Посаждане на растения
        while wurzelBot.hasEmptyFields():
            lowest = wurzelBot.getLowestVegetableStockEntry()
            if lowest == 'Your stock is empty':
                break
            Logger().print(i18n.t('wimpb.grow_plant_X', plant=lowest))
            planted = wurzelBot.growVegetablesInGardens(lowest)
            if planted == 0:
                lowestSingle = wurzelBot.getLowestSingleVegetableStockEntry()
                if lowestSingle == 'Your stock is empty':
                    break
                Logger().print(i18n.t('wimpb.grow_plant_X', plant=lowestSingle))
                wurzelBot.growVegetablesInGardens(lowestSingle)

        # Water plants
        # BG-Поливане на растенията
        time.sleep(3)
        Logger().print('')
        Logger().print(i18n.t('wimpb.watering_all_plants'))
        wurzelBot.water()

        # Claim Daily
        # BG-Събиране на дневният бонус
        Logger().print('')
        Logger().print(i18n.t('wimpb.claim_bonus'))
        wurzelBot.get_daily_bonuses()

        # Process Wimp Customers in Gardens
        # BG-Изпълни нуждите на Wimps в градините
        Logger().print('')
        Logger().print(i18n.t('wimpb.process_wimps'))
        wurzelBot.sell_to_wimps()

        # Collect decogarden points
        Logger().print('')
        Logger().print('Collecting decogardens...')
        wurzelBot.collect_decogardens()

        # Play minigames
        Logger().print('')
        Logger().print('Playing minigames...')
        wurzelBot.minigames.play()

        # Cut bonsais
        if wurzelBot.bonsaifarm is not None:
            Logger().print('')
            Logger().print('Cutting bonsais...')
            wurzelBot.cut_and_renew_bonsais(2)

        # Taking care of megafruit
        if wurzelBot.megafruit is not None:
            Logger().print('')
            Logger().print('Taking care of megafruit...')
            wurzelBot.check_megafruit()
    finally:
        # Close connection
        # BG-Затваряне на връзката
        Logger().print('')
        wurzelBot.logout()

if __name__ == "__main__":
    main()
