#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.Config import Config
from src.WurzelBot import WurzelBot
import i18n


"""
Example how the bot could be used
"""


# Logging? Set to True to enable or False to disable logging.
log = True

# Login data
user = ''
pw = ''
server = 46
lang = 'de' # e.g. en, de, ru
portalacc = False

i18n.load_path.append('lang')
i18n.set('locale', lang)
i18n.set('fallback', 'en')

# Init logger
if log:
    Config().log_to_stdout = True

# Init bot
wurzelBot = WurzelBot()
wurzelBot.login(server, user, pw, lang, portalacc)

# Collect daily login bonuses
wurzelBot.get_daily_bonuses()

# Play supported minigames
wurzelBot.minigames.play()

# Remove all weeds (weeds, stones, etc.) with all the money available
wurzelBot.remove_weeds()

# Harvest every plant that is ready for harvest in all gardens
wurzelBot.harvest()

# Grow the plant with the lowest stock
lowest = wurzelBot.getLowestVegetableStockEntry()
wurzelBot.growVegetablesInGardens(lowest)
# Grow the plant with the lowest stock that is 1x1
lowestSingle = wurzelBot.getLowestSingleVegetableStockEntry()
wurzelBot.growVegetablesInGardens(lowestSingle)
# Grow two salads in the garden
wurzelBot.growVegetablesInGardens('Salat', 2)
# Grow carrots until the stock is empty or if every field is filled
wurzelBot.growVegetablesInGardens('Karotte')

# Grow water plants
wurzelBot.growPlantsInAquaGardens('Wasserfeder')

# Water all plants in all gardens
wurzelBot.water()

# Sell to wimps
wurzelBot.sell_to_wimps()
# Sell to wimps and buy all missing plants from shops
# Warning: As the wimps pay less than it costs in the shops,
# this can end up with a financial loss
# wurzelBot.sell_to_wimps(buy_from_shop=True)

# Buy 1 salad from the shop
wurzelBot.shop.buy('Salat', 1) #buy plant with name and amount #BG-Купете растение по име и количество

# Send bees for 2 hours
# 1 = 2h, 2 = 8h, 3 = 24h
wurzelBot.send_bees(1) # Send bees for 2 hours

# Cut and renew bonsais
wurzelBot.cut_and_renew_bonsais()

# Try to do the next infinity quest
wurzelBot.infinityQuest()

# Logout
wurzelBot.logout()
