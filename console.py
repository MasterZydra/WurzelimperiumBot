from logging import log
import src.Main as wbot

# Login data
user = ''
pw = ''
server = 46

# Global vars
wurzelBot = object

def main():
    logo()
    init()
    
    while True:
        print('')
        userInput = input('▶ ').strip()
        inputLower = userInput.lower()

        if inputLower == 'exit': closeConnection()
        elif inputLower == 'harvest': harvest()
        elif inputLower == '?' or inputLower == 'help': help()
        elif inputLower.startswith('grow'): grow(userInput)
        elif inputLower == 'lowest': lowest()
        elif inputLower == 'stock': getStock()
        elif inputLower == 'water': water()
        else:
            print('Unknown command type \'help\' or \'?\' to see all available commands')


def logo():
    print('  _      __                 _____       __ ')
    print(' | | /| / /_ _________ ___ / / _ )___  / /_')
    print(' | |/ |/ / // / __/_ // -_) / _  / _ \/ __/')
    print(' |__/|__/\_,_/_/  /__/\__/_/____/\___/\__/ ')
    print('')

def init():
    print('Initialize WurzelBot...')
    
    if user == '' or pw == '':
        print('User and password not configured!\n')
        exit()
    
    global wurzelBot
    wurzelBot = wbot.initWurzelBot()
    wurzelBot.launchBot(server, user, pw)

def closeConnection():
    print('Close connection...\n')
    wurzelBot.exitBot()
    exit()

def help():
    print('Available commands:')
    print('-------------------')
    print('exit         Close connection and exit bot')
    print('grow         Grow a given plant')
    print('harvest      Harvest all gardens')
    print('help         Show all available commands')
    print('stock        Show all plants in stock')
    print('water        Water all plants')

def harvest():
    print('Harvest all gardens...')
    wurzelBot.harvestAllGarden()

def grow(argStr : str):
    argStr = argStr.replace('grow', '', 1).strip()
    args = argStr.split(' ')
    
    if len(args) > 2 or len(args) < 1 or args[0] == '' or (len(args) == 2 and not args[1].isnumeric()):
        print('Cannot parse input.')
        print('Expected format: grow [plant name] [opt. amount]')
    
    if len(args) == 1:
        print('Grow ' + args[0] + '...')
        wurzelBot.growPlantsInGardens(args[0])
    if len(args) == 2:
        print('Grow ' + args[1] + ' ' + args[0] + '...')
        wurzelBot.growPlantsInGardens(args[0], int(args[1]))

def lowest():
    print(wurzelBot.getLowestStockEntry())

def getStock():
    wurzelBot.printStock()

def water():
    print('Water all plants in all gardens...')
    wurzelBot.waterPlantsInAllGardens()

if __name__ == "__main__":
    main()