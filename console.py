from logging import log
import src.Logger as logger
from src.WurzelBot import WurzelBot
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
wurzelBot: WurzelBot = object

log = False
if args.logging != None:
    log = args.logging

i18n.load_path.append('lang')
i18n.set('locale', lang)
i18n.set('fallback', 'en')

def main():
    logo()
    init()
    logging()

    while True:
        print('')
        userInput = input('▶ ').strip()
        inputLower = userInput.lower()

        if inputLower == 'exit': closeConnection()
        elif inputLower == 'bee': bee()
        elif inputLower == 'harvest': harvest()
        elif inputLower == '?' or inputLower == 'help': help()
        elif inputLower.startswith('buy'): buy(userInput)
        elif inputLower.startswith('grow-water'): growWater(userInput)
        elif inputLower.startswith('grow'): grow(userInput)
        elif inputLower.startswith('lowest'): lowest(userInput)
        elif inputLower.startswith('stock'): getStock(userInput)
        elif inputLower == 'user': userData()
        elif inputLower == 'water': water()
        elif inputLower == 'weed': removeWeed()
        elif inputLower == 'bonus': getDailyLoginBonus()
        elif inputLower == 'wimp': processWimp()
        elif inputLower.startswith('details'): productDetails(userInput)
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

    global wurzelBot
    wurzelBot = WurzelBot()
    succ = wurzelBot.launchBot(server, user, pw, lang, portalacc)
    if succ != True:
        exit(-1)

def closeConnection():
    print(i18n.t('wimpb.close_connection'))
    print('')
    wurzelBot.exitBot()
    exit()

def help():
    print('Available commands:')
    print('-------------------')
    print('bee          Send bees')
    print('bonus        Get the daily login bonus')
    print('details      Show details to the products')
    print('             Opt. argument: "all", "water"')
    print('buy          Buy a given plant')
    print('exit         Close connection and exit bot')
    print('grow         Grow a given plant')
    print('grow-water   Grow a given water plant')
    print('harvest      Harvest all gardens')
    print('help         Show all available commands')
    print('lowest       Show the plant with the lowest stock (unequal zero)')
    print('             Opt. argument: "single", "water"')
    print('stock        Show all plants in stock')
    print('             Opt. argument: "sort"')
    print('user         Show details to the current user')
    print('water        Water all plants')
    print('weed         Remove all weed')
    print('wimp         Process Wimp Customers in Gardens')

def harvest():
    print('Harvest all gardens...')
    wurzelBot.harvestAllGarden()

def bee():
    print('Sending bees...')
    wurzelBot.sendBienen()

def buy(argStr : str):
    argStr = argStr.replace('buy', '', 1).strip()
    args = shlex.split(argStr)

    if len(args) != 2 or (len(args) == 2 and not args[1].isnumeric()):
        print('Cannot parse input.')
        print('Expected format: buy [plant name] [amount]')
        return

    print('Buying ' + args[1] + ' ' + args[0] + '...')
    wurzelBot.doBuyFromShop(args[0], int(args[1]))

def grow(argStr : str):
    argStr = argStr.replace('grow', '', 1).strip()
    args = shlex.split(argStr)

    if len(args) > 2 or len(args) < 1 or args[0] == '' or (len(args) == 2 and not args[1].isnumeric()):
        print('Cannot parse input.')
        print('Expected format: grow [plant name] [opt. amount]')
        return

    if len(args) == 1:
        print('Grow ' + args[0] + '...')
        wurzelBot.growVegetablesInGardens(args[0])
    if len(args) == 2:
        print('Grow ' + args[1] + ' ' + args[0] + '...')
        wurzelBot.growVegetablesInGardens(args[0], int(args[1]))

def growWater(argStr : str):
    argStr = argStr.replace('grow-water', '', 1).strip()
    args = shlex.split(argStr)

    if len(args) > 2 or len(args) < 1 or args[0] == '' or (len(args) == 2 and not args[1].isnumeric()):
        print('Cannot parse input.')
        print('Expected format: grow-water [plant name] [opt. amount]')
        return

    if len(args) == 1:
        print('Grow ' + args[0] + '...')
        wurzelBot.growPlantsInAquaGardens(args[0])
    if len(args) == 2:
        print('Grow ' + args[1] + ' ' + args[0] + '...')
        wurzelBot.growPlantsInAquaGardens(args[0], int(args[1]))

def lowest(argStr : str):
    argStr = argStr.replace('lowest', '', 1).strip()
    args = shlex.split(argStr)

    if len(args) > 1 or (len(args) == 1 and args[0] not in ['single', 'water'] and args[0] != ''):
        print('Cannot parse input.')
        print('Expected format: lowest [single|water]')
        return

    if len(args) == 0:
        print(wurzelBot.getLowestVegetableStockEntry())
    elif args[0] == 'single':
        print(wurzelBot.getLowestSingleVegetableStockEntry())
    elif args[0] == 'water':
        print(wurzelBot.getLowestWaterPlantStockEntry())

def getStock(argStr : str):
    argStr = argStr.replace('stock', '', 1).strip()
    args = shlex.split(argStr)

    if len(args) > 1 or (len(args) == 1 and args[0] != 'sort' and args[0] != ''):
        print('Cannot parse input.')
        print('Expected format: stock [sort]')
        return

    if len(args) == 0:
        wurzelBot.printStock()
    elif args[0] == 'sort':
        print(wurzelBot.get_ordered_stock_list())

def userData():
    colWidth = 20
    print('User:'.ljust(colWidth) + wurzelBot.user.get_username())
    print('Anzahl der Gärten:'.ljust(colWidth) + str(wurzelBot.user.get_number_of_gardens()))
    print('Level:'.ljust(colWidth) + str(wurzelBot.user.get_level()) + ' (' + wurzelBot.user.get_level_name() + ')')
    print('Bar:'.ljust(colWidth) + wurzelBot.user.get_bar_formatted())
    print('Points:'.ljust(colWidth) + f'{wurzelBot.user.get_points():,}'.replace(',', '.'))
    print('Coins:'.ljust(colWidth) + str(wurzelBot.user.get_coins()))

def water():
    print('Water all plants in all gardens...')
    wurzelBot.waterPlantsInAllGardens()

def productDetails(argStr : str):
    argStr = argStr.replace('details', '', 1).strip()
    args = shlex.split(argStr)

    if len(args) > 1 or (len(args) == 1 and args[0] not in ['all', 'water'] and args[0] != ''):
        print('Cannot parse input.')
        print('Expected format: details [all|water]')
        return

    if len(args) == 0:
        wurzelBot.printVegetableDetails()
    elif args[0] == 'all':
        wurzelBot.printProductDetails()
    elif args[0] == 'water':
        wurzelBot.printWaterPlantDetails()

def removeWeed():
    print(i18n.t('wimpb.remove_weed_from_all_gardens'))
    wurzelBot.removeWeedInAllGardens()

def getDailyLoginBonus():
    print('Claiming daily login bonus...')
    wurzelBot.get_daily_bonuses()

def processWimp():
    """Process Wimp Customers in Gardens"""
    print(i18n.t('wimpb.process_wimps'))
    wurzelBot.sellWimpsProducts(0, 0)

def logging():
    if log:
        logger.logger()

if __name__ == "__main__":
    main()
