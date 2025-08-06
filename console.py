from src.WurzelBot import WurzelBot
from src.core.Config import Config
from src.core.User import User
from src.product.Product import CATEGORY_WATER_PLANTS
import argparse
import i18n
import shlex

# Login data
# You can set them here or pass them as CLI arguments
server = 1
user = ''
pw = ''
lang = 'de' # de, en, bg
portalacc = False

parser = argparse.ArgumentParser()
parser.add_argument('--server', type=int, help='Server number')
parser.add_argument('--user', type=str, help='Username for login')
parser.add_argument('--password', type=str, help='Password for login')
parser.add_argument('--lang', type=str, help="Set Language and Region for the Game and Bot")
parser.add_argument('-p', '--portal', help="If -p or --portal Argument is passed, Portal Account Login will be used.", action='store_true', dest="portalacc")
parser.add_argument('-l', '--log', help="If -l or --log Argument is passed, logging will be enabled.", action='store_true', dest="logging")
args = parser.parse_args()

if args.server != None:
    server = args.server
if args.user != None:
    user = args.user
if args.password != None:
    pw = args.password
if args.lang != None:
    lang = args.lang
if args.portalacc != None:
    portalacc = args.portalacc

# Global vars
bot: WurzelBot = object

if args.logging:
    Config().log_to_stdout = True

i18n.load_path.append('lang')
i18n.set('locale', lang)
i18n.set('fallback', 'en')

def main():
    logo()
    init()

    while True:
        print('')
        user_input = input('▶ ').strip()
        inputLower = user_input.lower()

        if inputLower == 'exit': logout()
        elif inputLower.startswith('bee'): bee(user_input)
        elif inputLower.startswith('bonsai'): bonsai(user_input)
        elif inputLower == 'harvest': harvest()
        elif inputLower == '?' or inputLower == 'help': help()
        elif inputLower.startswith('buy'): buy(user_input)
        elif inputLower == 'games': games()
        elif inputLower.startswith('grow-water'): grow_aqua_garden(user_input)
        elif inputLower.startswith('grow'): grow(user_input)
        elif inputLower.startswith('lowest'): lowest(user_input)
        elif inputLower == 'megafruit': megafruit()
        elif inputLower.startswith('stock'): stock(user_input)
        elif inputLower == 'user': user_info()
        elif inputLower == 'water': water()
        elif inputLower == 'weed': remove_weeds()
        elif inputLower == 'bonus': getDailyLoginBonus()
        elif inputLower == 'wimp': wimp()
        elif inputLower.startswith('details'): productDetails(user_input)
        else:
            print('Unknown command type \'help\' or \'?\' to see all available commands')


def logo():
    print('  _      __                 _____       __ ')
    print(' | | /| / /_ _________ ___ / / _ )___  / /_')
    print(' | |/ |/ / // / __/_ // -_) / _  / _ \/ __/')
    print(' |__/|__/\_,_/_/  /__/\__/_/____/\___/\__/ ')
    print('')

def init():
    print(i18n.t('wimpb.initialize_bot'))

    if user == '' or pw == '' or portalacc == '':
        print(i18n.t('wimpb.login_credentials_not_configured'))
        print('')
        exit()

    global bot
    bot = WurzelBot()
    succ = bot.login(server, user, pw, lang, portalacc)
    if succ != True:
        exit(-1)

def logout():
    print(i18n.t('wimpb.close_connection'))
    print('')
    bot.logout()
    exit()

def help():
    print('Available commands:')
    print('-------------------')
    print('bee          Send bees')
    print('             Opt. argument: "2h" (default), "8h", "24h"')
    print('bonsai       Cut all branches and renew bonsais')
    print('             Opt. argument: 2 (default level) - 10')
    print('bonus        Get the daily login bonus')
    print('details      Show details to the products')
    print('             Opt. argument: "all", "water"')
    print('buy          Buy a given plant')
    print('exit         Close connection and exit bot')
    print('games        Play the minigames')
    print('grow         Grow a given plant')
    print('grow-water   Grow a given water plant')
    print('harvest      Harvest all gardens')
    print('help         Show all available commands')
    print('lowest       Show the plant with the lowest stock (unequal zero)')
    print('             Opt. argument: "single", "water"')
    print('megafruit    Take care of megafruits')
    print('stock        Show all plants in stock')
    print('             Opt. argument: "sort", "water"')
    print('user         Show details to the current user')
    print('water        Water all plants')
    print('weed         Remove all weed')
    print('wimp         Process Wimp Customers in Gardens')

def harvest():
    print('Harvest all gardens...')
    bot.harvest()

def bee(arg_str : str):
    arg_str = arg_str.replace('bee', '', 1).strip()
    args = shlex.split(arg_str)

    if len(args) > 1 or (len(args) == 1 and args[0] not in ['2h', '8h', '24h'] and args[0] != ''):
        print('Cannot parse input.')
        print('Expected format: bee [2h|8h|24h]')
        return

    tour = 1
    if len(args) == 0:
        args.append('2h')
        tour = 1
    elif args[0] == '2h':
        tour = 1
    elif args[0] == '8h':
        tour = 2
    elif args[0] == '24h':
        tour = 3

    print(f'Sending bees for {args[0]}...')
    bot.send_bees(tour)

def bonsai(arg_str : str):
    arg_str = arg_str.replace('bonsai', '', 1).strip()
    args = shlex.split(arg_str)

    if len(args) > 1 or (len(args) == 1 and args[0] not in ['2', '3', '4', '5', '6', '7', '8', '9', '10'] and args[0] != ''):
        print('Cannot parse input.')
        print('Expected format: bonsai [2|3|4|...|10]')
        return

    finish_level = 2
    if len(args) == 0:
        finish_level = 2
    else:
        finish_level = int(args[0])

    print(f'Cutting bonsais...')
    bot.cut_and_renew_bonsais(finish_level)

def buy(arg_str : str):
    arg_str = arg_str.replace('buy', '', 1).strip()
    args = shlex.split(arg_str)

    if len(args) != 2 or (len(args) == 2 and not args[1].isnumeric()):
        print('Cannot parse input.')
        print('Expected format: buy [plant name] [amount]')
        return

    print('Buying ' + args[1] + ' ' + args[0] + '...')
    bot.shop.buy(args[0], int(args[1]))

def games():
    print('Playing minigames...')
    bot.minigames.play()

def grow(arg_str : str):
    arg_str = arg_str.replace('grow', '', 1).strip()
    args = shlex.split(arg_str)

    if len(args) > 2 or len(args) < 1 or args[0] == '' or (len(args) == 2 and not args[1].isnumeric()):
        print('Cannot parse input.')
        print('Expected format: grow [plant name] [opt. amount]')
        return

    if len(args) == 1:
        print('Grow ' + args[0] + '...')
        bot.growVegetablesInGardens(args[0])
    if len(args) == 2:
        print('Grow ' + args[1] + ' ' + args[0] + '...')
        bot.growVegetablesInGardens(args[0], int(args[1]))

def grow_aqua_garden(arg_str : str):
    arg_str = arg_str.replace('grow-water', '', 1).strip()
    args = shlex.split(arg_str)

    if len(args) > 2 or len(args) < 1 or args[0] == '' or (len(args) == 2 and not args[1].isnumeric()):
        print('Cannot parse input.')
        print('Expected format: grow-water [plant name] [opt. amount]')
        return

    if len(args) == 1:
        print('Grow ' + args[0] + '...')
        bot.growPlantsInAquaGardens(args[0])
    if len(args) == 2:
        print('Grow ' + args[1] + ' ' + args[0] + '...')
        bot.growPlantsInAquaGardens(args[0], int(args[1]))

def lowest(arg_str : str):
    arg_str = arg_str.replace('lowest', '', 1).strip()
    args = shlex.split(arg_str)

    if len(args) > 1 or (len(args) == 1 and args[0] not in ['single', 'water'] and args[0] != ''):
        print('Cannot parse input.')
        print('Expected format: lowest [single|water]')
        return

    if len(args) == 0:
        print(bot.getLowestVegetableStockEntry())
    elif args[0] == 'single':
        print(bot.getLowestSingleVegetableStockEntry())
    elif args[0] == 'water':
        print(bot.getLowestWaterPlantStockEntry())

def megafruit():
    print('Taking care of megafruit...')
    bot.check_megafruit()

def stock(arg_str : str):
    arg_str = arg_str.replace('stock', '', 1).strip()
    args = shlex.split(arg_str)

    if len(args) > 1 or (len(args) == 1 and args[0] not in ['sort', 'water'] and args[0] != ''):
        print('Cannot parse input.')
        print('Expected format: stock [sort|water]')
        return

    if len(args) == 0:
        bot.printStock()
    elif args[0] == 'water':
        bot.printStock(CATEGORY_WATER_PLANTS)
    elif args[0] == 'sort':
        print(bot.get_ordered_stock_list())

def user_info():
    colWidth = 20
    print('User:'.ljust(colWidth) + User().get_username())
    print('Anzahl der Gärten:'.ljust(colWidth) + str(User().get_number_of_gardens()))
    print('Level:'.ljust(colWidth) + str(User().get_level()) + ' (' + User().get_level_name() + ')')
    print('Bar:'.ljust(colWidth) + User().get_bar_formatted())
    print('Points:'.ljust(colWidth) + f'{User().get_points():,}'.replace(',', '.'))
    print('Coins:'.ljust(colWidth) + str(User().get_coins()))

def water():
    print('Water all plants in all gardens...')
    bot.water()

def productDetails(arg_str : str):
    arg_str = arg_str.replace('details', '', 1).strip()
    args = shlex.split(arg_str)

    if len(args) > 1 or (len(args) == 1 and args[0] not in ['all', 'water'] and args[0] != ''):
        print('Cannot parse input.')
        print('Expected format: details [all|water]')
        return

    if len(args) == 0:
        bot.printVegetableDetails()
    elif args[0] == 'all':
        bot.printProductDetails()
    elif args[0] == 'water':
        bot.printWaterPlantDetails()

def remove_weeds():
    print(i18n.t('wimpb.remove_weed_from_all_gardens'))
    bot.remove_weeds()

def getDailyLoginBonus():
    print('Claiming daily login bonus...')
    bot.get_daily_bonuses()

def wimp():
    """Process Wimp Customers in Gardens"""
    print(i18n.t('wimpb.process_wimps'))
    bot.sell_to_wimps()

if __name__ == "__main__":
    main()
