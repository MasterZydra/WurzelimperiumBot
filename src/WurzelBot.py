#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 21.03.2017

@author: MrFlamez
'''

from collections import Counter
from src.Bonsai import Bonsai
from src.bonus.Bonus import Bonus
from src.core.Config import Config
from src.core.HTTPCommunication import HTTPConnection
from src.core.Login import Login
from src.core.Feature import Feature
from src.Garten import Garden, AquaGarden, HerbGarden
from src.honey.Honey import Honey
from src.stock.Stock import Stock
from src.marketplace.Marketplace import Marketplace
from src.Messenger import Messenger
from src.note.Note import Note
from src.product.ProductData import ProductData
from src.quest.Quest import Quest
from src.shop.ShopProducts import ShopProducts
from src.citypark.CityPark import CityPark
from src.core.User import User
from src.wimp.Wimp import Wimp
import logging, i18n, datetime

i18n.load_path.append('lang')

class WurzelBot(object):
    """
    Die Klasse WurzelBot übernimmt jegliche Koordination aller anstehenden Aufgaben.
    """
    #BG- """ Класът WurzelBot се грижи за координацията на всички предстоящи задачи."""


    def __init__(self):
        self.__config = Config()
        self.__logBot = logging.getLogger("bot")
        self.__logBot.setLevel(logging.DEBUG)
        self.__HTTPConn = HTTPConnection()
        self.feature = Feature()
        self.productData = ProductData()
        self.user = User()
        self.messenger = Messenger(self.__HTTPConn)
        self.stock = Stock()
        self.garten = []
        self.wassergarten = None
        self.herbgarden = None
        self.honey = None
        self.bonsaifarm = None
        self.marketplace = Marketplace()
        self.wimparea = Wimp()
        self.quest = Quest()
        self.bonus = Bonus()
        self.note = Note()
        self.park = None


    def __initGardens(self):
        """Ermittelt die Anzahl der Gärten und initialisiert alle."""
        #BG-"""Определя броя на градините и ги инициализира всички."""

        try:
            for i in range(1, self.user.get_number_of_gardens() + 1):
                self.garten.append(Garden(self.__HTTPConn, i))

            if self.feature.is_aqua_garden_available() is True:
                self.wassergarten = AquaGarden(self.__HTTPConn)

            if self.feature.is_herb_garden_available() is True:
                self.herbgarden = HerbGarden(self.__HTTPConn)

            if self.feature.is_honey_farm_available() is True:
                self.honey = Honey()

            if self.feature.is_bonsai_farm_available() is True:
                self.bonsaifarm = Bonsai(self.__HTTPConn)

            if self.feature.is_city_park_available() is True:
                self.park = CityPark()

        except:
            raise


    def __getAllFieldIDsFromFieldIDAndSizeAsString(self, fieldID, sx, sy):
        """
        Rechnet anhand der fieldID und Größe der Pflanze (sx, sy) alle IDs aus und gibt diese als String zurück.
        """
        #BG-Изчислява всички идентификационни номера чрез fieldID и размера на растението (sx, sy) и ги връща като низ.

        if (sx == '1' and sy == '1'): return str(fieldID)
        if (sx == '2' and sy == '1'): return str(fieldID) + ',' + str(fieldID + 1)
        if (sx == '1' and sy == '2'): return str(fieldID) + ',' + str(fieldID + 17)
        if (sx == '2' and sy == '2'): return str(fieldID) + ',' + str(fieldID + 1) + ',' + str(fieldID + 17) + ',' + str(fieldID + 18)
        self.__logBot.debug(f'Error der plantSize --> sx: {sx} sy: {sy}')


    def __getAllFieldIDsFromFieldIDAndSizeAsIntList(self, fieldID, sx, sy):
        """
        Rechnet anhand der fieldID und Größe der Pflanze (sx, sy) alle IDs aus und gibt diese als Integer-Liste zurück.
        """
        #BG-Изчислява всички идентификационни номера чрез fieldID и размера на растението (sx, sy) и ги връща като списък от цели числа.

        sFields = self.__getAllFieldIDsFromFieldIDAndSizeAsString(fieldID, sx, sy)
        listFields = sFields.split(',') #Stringarray

        for i in range(0, len(listFields)):
            listFields[i] = int(listFields[i])

        return listFields


    def launchBot(self, server, user, pw, lang, portalacc) -> bool:
        """
        Diese Methode startet und initialisiert den Wurzelbot. Dazu wird ein Login mit den
        übergebenen Logindaten durchgeführt und alles nötige initialisiert.
        """
        #BG-Този метод стартира и инициализира Wurzelbot. За целта се извършва вход с предоставените данни за влизане и се инициализира всичко необходимо.

        self.__logBot.info('-------------------------------------------')
        self.__logBot.info(f'Starting Wurzelbot for User {user} on Server No. {server}')
        loginDaten = Login(server=server, user=user, password=pw, language=lang)

        if portalacc == True:
            try:
                self.__HTTPConn.logInPortal(loginDaten)
            except Exception as e:
                if self.__config.isDevMode:
                    raise e
                self.__logBot.error(i18n.t('wimpb.error_starting_wbot'))
                return False
        else:
            try:
                self.__HTTPConn.logIn(loginDaten)
            except Exception as e:
                if self.__config.isDevMode:
                    raise e
                self.__logBot.error(i18n.t('wimpb.error_starting_wbot'))
                return False

        try:
            self.user.update()
        except Exception as e:
            if self.__config.isDevMode:
                raise e
            self.__logBot.error(i18n.t('wimpb.error_refresh_userdata'))
            return False

        try:
            self.__initGardens()
        except Exception as e:
            if self.__config.isDevMode:
                raise e
            self.__logBot.error(i18n.t('wimpb.error_number_of_gardens'))
            return False

        self.user.accountLogin = loginDaten
        self.productData.init()
        self.stock.init_product_list(self.productData.get_product_id_list())
        self.stock.update()
        return True


    def exitBot(self):
        """Beendet den Wurzelbot geordnet und setzt alles zurück."""
        #BG-"""Завършва Wurzelbot подредено и нулира всичко."""

        self.__logBot.info(i18n.t('wimpb.exit_wbot'))
        try:
            self.__HTTPConn.logOut()
            self.__logBot.info(i18n.t('wimpb.logout_success'))
            self.__logBot.info('-------------------------------------------')
        except Exception as e:
            if self.__config.isDevMode:
                raise e
            self.__logBot.error(i18n.t('wimpb.exit_wbot_abnormal'))


    def updateUserData(self):
        """Ermittelt die Userdaten und setzt sie in der Spielerklasse."""
        #BG-"""Определя потребителските данни и ги задава в класа на играча."""

        try:
            self.user.userData = self.__HTTPConn.readUserDataFromServer()
        except:
            self.__logBot.error(i18n.t('wimpb.error_refresh_userdata'))


    def waterPlantsInAllGardens(self):
        """Alle Gärten des Spielers werden komplett bewässert."""
        #BG-"""Всички градини на играча се поливат напълно."""

        garden: Garden
        for garden in self.garten:
            garden.waterPlants()

        if self.feature.is_aqua_garden_available():
            self.wassergarten.waterPlants()


    def writeMessagesIfMailIsConfirmed(self, recipients, subject, body):
        """
        Erstellt eine neue Nachricht, füllt diese aus und verschickt sie.
        recipients muss ein Array sein!.
        Eine Nachricht kann nur verschickt werden, wenn die E-Mail Adresse bestätigt ist.
        """
        #BG-Създава ново съобщение, попълва го и го изпраща.Получателите трябва да са в масив! Съобщение може да бъде изпратено само ако електронната поща е потвърдена.

        if (self.user.is_mail_confirmed()):
            try:
                self.messenger.writeMessage(self.user.get_username(), recipients, subject, body)
            except:
                self.__logBot.error(i18n.t('wimpb.no_message'))

    def getEmptyFieldsOfGardens(self):
        """
        Gibt alle leeren Felder aller normalen Gärten zurück.
        Kann dazu verwendet werden zu entscheiden, wie viele Pflanzen angebaut werden können.
        """
        #BG-Връща всички празни полета във всички обикновени градини. Може да се използва за вземане на решение колко растения могат да бъдат засадени.

        emptyFields = []
        try:
            for garden in self.garten:
                emptyFields.append(garden.getEmptyFields())
        except:
            self.__logBot.error(f'Could not determinate empty fields from garden {garden.getID()}.')
        return emptyFields

    def getGrowingPlantsInGardens(self):
        growingPlants = Counter()
        try:
            for garden in self.garten:
                growingPlants.update(garden.getGrowingPlants())
        except:
            self.__logBot.error('Could not determine growing plants of garden ' + str(garden.getID()) + '.')

        return dict(growingPlants)

    # Wimps
    def get_all_wimps_products(self) -> dict:
        allWimpsProducts = Counter()
        for garden in self.garten:
            tmpWimpData = self.wimparea.get_wimps_data(garden)
            for products in tmpWimpData.values():
                allWimpsProducts.update(products[1])

        if self.wassergarten:
            tmpWimpData = self.wimparea.get_wimps_data_watergarden()
            for products in tmpWimpData.values():
                allWimpsProducts.update(products[1])

        return dict(allWimpsProducts)

    def sell_to_wimps(self, max_amount=100):
        self.user.load_data()
        points_before = self.user.get_points()

        stock_list = self.stock.get_ordered_stock_list()
        wimps_data = []
        rewards = 0
        npc_price = 0
        counter = 0

        for garden in self.garten:
            for k, v in self.wimparea.get_wimps_data(garden).items():
                wimps_data.append({k: v})

        if self.wassergarten:
            for k, v in self.wimparea.get_wimps_data_watergarden().items():
                wimps_data.append({k: v})

        if not wimps_data:
            self.__logBot.info(f"No wimps available!")
            return -1

        for wimps in wimps_data:
            for wimp, products in wimps.items():
                if not self.check_wimps_profitable(products, max_amount):
                    self.wimparea.decline(wimp)
                    self.__logBot.info(f"Declined wimp: {wimp}")
                else:
                    check, stock_list = self.check_wimps_required_amount(products[1], stock_list, minimal_balance = 500)
                    if check:
                        rewards += products[0]
                        counter += 1
                        self.__logBot.info(f"Selling products to wimp: {wimp}")
                        new_products_counts = self.wimparea.sell(wimp)
                        for id, amount in products[1].items():
                            stock_list[id] -= amount
                            npc_price += self.productData.get_product_by_id(id).get_price_npc() * amount
        
        self.user.load_data()
        points_after = self.user.get_points()
        points_gained = points_after - points_before
        self.__logBot.info(f"Gained {points_gained} points.")
        self.__logBot.info(f"Sold to {counter} wimps for {rewards:.2f} wT (equals {(rewards/npc_price):.2%} of Shop-price: {npc_price:.2f} wT)")

        sales, revenue = self.__HTTPConn.getInfoFromStats('Wimps')
        self.__logBot.info(f"Stats--------------------------------\n"
                           f"WIMP-sales  : {sales}\n"
                           f"WIMP-revenue: {revenue}\n"
                           f"-------------------------------------"
                          )

    def check_wimps_profitable(self, products, max_amount) -> bool:
        # Check if the price the wimp wants to pay is more than the price of buying every product in the shops.
        #BG-Проверява дали цената, която мамата иска да плати, е по-голяма от цената за закупуване на всеки продукт в магазините.

        # If the profit in percent is greater or equal to the given value, the return value is True.
        #BG-Ако печалбата в проценти е по-голяма или равна на предоставената стойност, връщаемата стойност е True

        # TODO How to calculate profitability? It seems that none of the wimps is profitable when using the shop prices.
        #BG-TODO Как да изчислявам печалбата? Изглежда, че нито един от „wimps“ не е печеливш, когато се използват цените от магазините.

        # this is just my personal choice. When the amount of a product <= 100 you get nearly 2/3 of the WIMP-baseprice --> that's acceptable for me
        for id, amount in products[1].items():
            if amount > max_amount:
                return False
        return True
    
    def check_wimps_required_amount(self, products, stock_list, minimal_balance):
        for id, amount in products.items():
            product = self.productData.get_product_by_id(id)
            min_stock = max(self.note.get_min_stock(), self.note.get_min_stock(product.get_name()), minimal_balance)
            if stock_list.get(id, None) < amount + min_stock or self.user.get_level() < 3:
                if self.doBuyFromShop(int(id), minimal_balance) == -1:
                    return False, stock_list
                stock_list[id] += minimal_balance
            return True, stock_list

    def getNextRunTime(self):
        garden_time = []
        for garden in self.garten:
            garden_time.append(garden.getNextWaterHarvest())

        self.updateUserData()
        human_time = datetime.datetime.fromtimestamp(min(garden_time))
        print(f"Next time water/harvest: {human_time.strftime('%d/%m/%y %H:%M:%S')} ({min(garden_time)})")
        return min(garden_time)

    def hasEmptyFields(self):
        emptyFields = self.getEmptyFieldsOfGardens()
        amount = 0
        for garden in emptyFields:
            amount += len(garden)

        return amount > 0

    def getWeedFieldsOfGardens(self):
        """Gibt alle Unkrau-Felder aller normalen Gärten zurück."""
        #BG- Връща всички полета с плевели във всички обикновени градини.
        weedFields = []
        try:
            for garden in self.garten:
                weedFields.append(garden.getWeedFields())
        except:
            self.__logBot.error(f'Could not determinate weeds on fields of garden {garden.getID()}.')

        return weedFields

    def harvestAllGarden(self):
        try:
            for garden in self.garten:
                garden.harvest()

            if self.feature.is_aqua_garden_available():
                self.wassergarten.harvest()
                pass

            self.stock.update()
            self.__logBot.info(i18n.t('wimpb.harvest_successful'))
        except:
            self.__logBot.error(i18n.t('wimpb.harvest_not_successful'))

    def growVegetablesInGardens(self, productName, amount=-1):
        """
        Pflanzt so viele Pflanzen von einer Sorte wie möglich über alle Gärten hinweg an.
        """
        #BG-Засажда колкото е възможно повече растения от определен вид през всички градини.
        planted = 0

        product = self.productData.get_product_by_name(productName)

        if product is None:
            logMsg = f'Plant "{productName}" not found'
            self.__logBot.error(logMsg)
            print(logMsg)
            return -1

        if not product.is_vegetable() or not product.is_plantable():
            logMsg = f'"{productName}" could not be planted'
            self.__logBot.error(logMsg)
            print(logMsg)
            return -1

        if amount == -1 or amount > self.stock.get_stock_by_product_id(product.get_id()):
            amount = self.stock.get_stock_by_product_id(product.get_id())

        remainingAmount = amount
        garden: Garden
        for garden in self.garten:
            planted += garden.growPlant(product.get_id(), product.get_sx(), product.get_sy(), remainingAmount)
            remainingAmount = amount - planted

        self.stock.update()

        return planted

    def growPlantsInAquaGardens(self, productName, amount=-1):
        """
        Pflanzt so viele Pflanzen von einer Sorte wie möglich über alle Gärten hinweg an.
        """
        #BG-Засаждане на възможно най-много растения от определен вид през всички градини.
        if self.feature.is_aqua_garden_available():
            planted = 0
            product = self.productData.get_product_by_name(productName)
            if product is None:
                logMsg = f'Plant "{productName}" not found'
                self.__logBot.error(logMsg)
                print(logMsg)
                return -1

            if not product.is_water_plant() or not product.is_plantable():
                logMsg = f'"{productName}" could not be planted'
                self.__logBot.error(logMsg)
                print(logMsg)
                return -1

            if amount == -1 or amount > self.stock.get_stock_by_product_id(product.get_id()):
                amount = self.stock.get_stock_by_product_id(product.get_id())
            remainingAmount = amount
            planted += self.wassergarten.growPlant(product.get_id(), product.get_sx(), product.get_sy(), product.get_edge(), remainingAmount)
            self.stock.update()

            return planted

    def printStock(self):
        isSmthPrinted = False
        for productID in self.stock.get_keys():
            product = self.productData.get_product_by_id(productID)

            amount = self.stock.get_stock_by_product_id(productID)
            if amount == 0: continue

            print(str(product.get_name()).ljust(30) + 'Amount: ' + str(amount).rjust(5))
            isSmthPrinted = True

        if not isSmthPrinted:
            print('Your stock is empty')

    def get_lowest_stock_entry(self):
        entryID = self.stock.get_lowest_stock_entry()
        if entryID == -1: return 'Your stock is empty'
        return self.productData.get_product_by_id(entryID).get_name()

    def get_ordered_stock_list(self):
        orderedList = ''
        for productID in self.stock.get_ordered_stock_list():
            orderedList += str(self.productData.get_product_by_id(productID).get_name()).ljust(20)
            orderedList += str(self.stock.get_ordered_stock_list()[productID]).rjust(5)
            orderedList += str('\n')
        return orderedList.strip()

    def getLowestVegetableStockEntry(self):
        # Grow only plants
        plantOnly = self.note.get_grow_only()
        if len(plantOnly) != 0:
            for productID in self.stock.get_ordered_stock_list():
                if self.productData.get_product_by_id(productID).get_name() in plantOnly:
                    return self.productData.get_product_by_id(productID).get_name()

            return 'Your stock is empty'

        # Default behaviour
        lowestStock = -1
        lowestProductId = -1
        for productID in self.stock.get_ordered_stock_list():
            if not self.productData.get_product_by_id(productID).is_vegetable() or \
                not self.productData.get_product_by_id(productID).is_plantable():
                continue

            currentStock = self.stock.get_stock_by_product_id(productID)
            if lowestStock == -1 or currentStock < lowestStock:
                lowestStock = currentStock
                lowestProductId = productID
                continue

        if lowestProductId == -1: return 'Your stock is empty'
        return self.productData.get_product_by_id(lowestProductId).get_name()

    def getLowestSingleVegetableStockEntry(self):
        lowestSingleStock = -1
        lowestSingleProductId = -1
        for productID in self.stock.get_ordered_stock_list():
            if not self.productData.get_product_by_id(productID).is_vegetable() or \
                not self.productData.get_product_by_id(productID).is_plantable() or \
                not self.productData.get_product_by_id(productID).get_name() in self.productData.get_single_field_vegetable_list():
                continue

            currentStock = self.stock.get_stock_by_product_id(productID)
            if lowestSingleStock == -1 or currentStock < lowestSingleStock:
                lowestSingleStock = currentStock
                lowestSingleProductId = productID
                continue

        if lowestSingleProductId == -1: return 'Your stock is empty'
        return self.productData.get_product_by_id(lowestSingleProductId).get_name()

    def getLowestWaterPlantStockEntry(self):
        lowestStock = -1
        lowestProductId = -1
        for productID in self.stock.get_ordered_stock_list():
            if not self.productData.get_product_by_id(productID).is_water_plant() or \
                not self.productData.get_product_by_id(productID).is_plantable():
                continue

            currentStock = self.stock.get_stock_by_product_id(productID)
            if lowestStock == -1 or currentStock < lowestStock:
                lowestStock = currentStock
                lowestProductId = productID
                continue

        if lowestProductId == -1: return 'Your stock is empty'
        return self.productData.get_product_by_id(lowestProductId).get_name()

    def printProductDetails(self):
        self.productData.print_all()

    def printVegetableDetails(self):
        self.productData.print_all_vegetables()

    def printWaterPlantDetails(self):
        self.productData.print_all_water_plants()

    def removeWeedInAllGardens(self):
        """Entfernt Unkraut/Maulwürfe/Steine aus allen Gärten."""
        #BG-Премахва плевели, кърлежи и камъни от всички градини.
        #TODO: Wassergarten ergänzen
        try:
            for garden in self.garten:
                garden.removeWeed()
            self.__logBot.info(i18n.t('wimpb.w_harvest_successful'))
        except:
            self.__logBot.error(i18n.t('wimpb.w_harvest_not_successful'))

    def get_daily_bonuses(self):
        self.bonus.get_daily_login_bonus()

        if self.user.is_premium_active():
            self.bonus.collect_bonus_item_points()

        if self.user.is_guild_member():
            self.bonus.collect_lucky_mole()

    def infinityQuest(self, MINwt):
        #TODO: Mehr Checks bzw Option wieviele Quests/WT man ausgeben mag - da es kein cooldown gibt! (hoher wt verlust)
        if self.user.get_bar() < MINwt:
            print('Zuwenig WT')
            pass
        if self.user.get_level() > 23 and self.user.get_bar() > MINwt:
            questnr = self.__HTTPConn.initInfinityQuest()['questnr']
            if int(questnr) <= 500:
                for item in self.__HTTPConn.initInfinityQuest()['questData']['products']:
                    #print(item)
                    product = item['pid']
                    product = self.productData.get_product_by_id(product)
                    #print(f'Pid {product.get_id()}')
                    needed = item['amount']
                    stored = self.stock.get_stock_by_product_id(product.get_id())
                    #print(f'stored {stored}')
                    if needed >= stored:
                        missing = abs(needed - stored) + 10
                        #print(f'missing {missing}')
                        self.doBuyFromShop(product.get_id(),missing)
                    try:
                        self.__HTTPConn.sendInfinityQuest(questnr, product.get_id(), needed)
                    except:
                        pass

    # Shops
    #BG- Магазини
    def doBuyFromShop(self, productName, amount: int):
        if type(productName) is int:
            productName = self.productData.get_product_by_id(productName).get_name()

        product = self.productData.get_product_by_name(productName)
        if product is None:
            logMsg = f'Plant "{productName}" not found'
            self.__logBot.error(logMsg)
            print(logMsg)
            return -1

        productId = product.get_id()

        Shop = None
        for k, id in ShopProducts.products().items():
            if productName in k:
                Shop = id
                break
        if Shop in [1,2,3,4]:
            try:
                self.__HTTPConn.buyFromShop(Shop, productId, amount)
            except:
                pass
        elif Shop == 0:
            try:
                self.__HTTPConn.buyFromAquaShop(productId, amount)
            except:
                pass
        return 0

    # Bienen
    #BG- Пчели
    def sendBienen(self):
        #TODO prüfen ob wirklich gesendet wurde, ansonsten Befehl wiederholen
        """
        Probiert alle Bienen für Zeitoption 1 (ohne Verkürzung 2h) zu senden
        """
        #BG-Пробва да изпрати всички пчели за времева опция 1 (без намаляване 2 часа).
        if self.feature.is_honey_farm_available():
            self.honey.start_all_hives()
            self.honey.fill_honey()
        else:
            logMsg = 'Konnte nicht alle Bienen ernten.'
            print(logMsg)
            self.__logBot.error(logMsg)

    # Bonsai
    def cutAndRenewBonsais(self):
        """cut all branches and renew bonsais if lvl 2"""
        #BG-Ако нивото е 2, отрежи всички клони и поднови бонсаите.
        self.bonsaifarm.cutAllBonsai()
        self.bonsaifarm.checkBonsai()
        self.bonsaifarm.cutAllBonsai()

    # City park
    def check_park(self):
        """automate Park: first collect the cashpoint, then check if any item has to be renewed"""
        self.park.collect_cash_from_cashpoint()
        self.park.renew_all_items()

    # Herb garden
    def check_herb_garden(self):
        if self.feature.is_herb_garden_available() is not True:
            return

        self.herbgarden.remove_weed()
        self.herbgarden.harvest()
        self.herbgarden.grow_plant(self)
