#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 21.03.2017

@author: MrFlamez
'''

from src.bonsai.Bonsai import Bonsai
from src.bonus.Bonus import Bonus
from src.citypark.CityPark import CityPark
from src.core.Config import Config
from src.core.Feature import Feature
from src.core.HTTPCommunication import HTTPConnection
from src.core.Login import Login
from src.core.User import User
from src.garden.aqua.AquaGarden import AquaGarden
from src.garden.Garden import Garden
from src.garden.herb.HerbGarden import HerbGarden
from src.greenhouse.Greenhouse import Greenhouse
from src.honey.Honey import Honey
from src.marketplace.Marketplace import Marketplace
from src.message.Messenger import Messenger
from src.minigames.Minigames import Minigames
from src.note.Note import Note
from src.product.ProductData import ProductData
from src.quest.Quest import Quest
from src.shop.Shop import Shop
from src.stock.Stock import Stock
from src.wimp.Wimp import Wimp
from collections import Counter
import logging, i18n, datetime

i18n.load_path.append('lang')

class WurzelBot:
    """
    Die Klasse WurzelBot übernimmt jegliche Koordination aller anstehenden Aufgaben.
    """
    #BG- """ Класът WurzelBot се грижи за координацията на всички предстоящи задачи."""


    def __init__(self):
        self.__logBot = logging.getLogger("bot")
        self.__logBot.setLevel(logging.DEBUG)
        self.__HTTPConn = HTTPConnection()
        self.messenger = Messenger()
        self.shop = Shop()
        self.gardens = []
        self.aquagarden = None
        self.herbgarden = None
        self.honey = None
        self.bonsaifarm = None
        self.marketplace = Marketplace()
        self.wimparea = Wimp()
        self.quest = Quest()
        self.bonus = Bonus()
        self.note = None
        self.park = None
        self.greenhouse = None
        self.minigames = Minigames()


    def __init_gardens(self):
        """Ermittelt die Anzahl der Gärten und initialisiert alle."""
        #BG-"""Определя броя на градините и ги инициализира всички."""

        try:
            for i in range(1, User().get_number_of_gardens() + 1):
                self.gardens.append(Garden(i))

            if Feature().is_aqua_garden_available():
                self.aquagarden = AquaGarden()

            if Feature().is_herb_garden_available():
                self.herbgarden = HerbGarden()

            if Feature().is_honey_farm_available():
                self.honey = Honey()

            if Feature().is_bonsai_farm_available():
                self.bonsaifarm = Bonsai()

            if Feature().is_city_park_available():
                self.park = CityPark()

            if Feature().is_greenhouse_available():
                self.greenhouse = Greenhouse()
            
            if Feature().is_note_available():
                self.note = Note()

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


    def login(self, server, user, pw, lang, portalacc) -> bool:
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
                if Config().isDevMode:
                    raise e
                self.__logBot.error(i18n.t('wimpb.error_starting_wbot'))
                return False
        else:
            try:
                self.__HTTPConn.logIn(loginDaten)
            except Exception as e:
                if Config().isDevMode:
                    raise e
                self.__logBot.error(i18n.t('wimpb.error_starting_wbot'))
                return False

        try:
            User().update()
        except Exception as e:
            if Config().isDevMode:
                raise e
            self.__logBot.error(i18n.t('wimpb.error_refresh_userdata'))
            return False

        try:
            self.__init_gardens()
        except Exception as e:
            if Config().isDevMode:
                raise e
            self.__logBot.error(i18n.t('wimpb.error_number_of_gardens'))
            return False

        User().accountLogin = loginDaten
        ProductData().init()
        Stock().init_product_list(ProductData().get_product_id_list())
        Stock().update()
        return True


    def logout(self):
        """Exit the bot cleanly with login and reset the data"""
        self.__logBot.info(i18n.t('wimpb.exit_wbot'))
        try:
            self.__HTTPConn.logOut()
            self.__logBot.info(i18n.t('wimpb.logout_success'))
            self.__logBot.info('-------------------------------------------')
        except Exception as e:
            if Config().isDevMode:
                raise e
            self.__logBot.error(i18n.t('wimpb.exit_wbot_abnormal'))

    def get_stop_bot_note(self) -> bool:
        """Check notes for stop bot entry"""
        if not Feature().is_note_available():
            return False

        return self.note.get_stop_bot()

    def water(self):
        """Waters all of the player's gardens"""
        garden: Garden
        for garden in self.gardens:
            garden.water()

        if Feature().is_aqua_garden_available():
            self.aquagarden.water()

    def writeMessageIfMailIsConfirmed(self, recipients, subject, body):
        """
        Erstellt eine neue Nachricht, füllt diese aus und verschickt sie.
        recipients muss ein Array sein!.
        Eine Nachricht kann nur verschickt werden, wenn die E-Mail Adresse bestätigt ist.
        """
        #BG-Създава ново съобщение, попълва го и го изпраща.Получателите трябва да са в масив! Съобщение може да бъде изпратено само ако електронната поща е потвърдена.

        if (User().is_mail_confirmed()):
            try:
                self.messenger.write(recipients, subject, body)
            except Exception:
                self.__logBot.error(i18n.t('wimpb.no_message'))

    def get_empty_fields(self):
        """
        Gibt alle leeren Felder aller normalen Gärten zurück.
        Kann dazu verwendet werden zu entscheiden, wie viele Pflanzen angebaut werden können.
        """
        #BG-Връща всички празни полета във всички обикновени градини. Може да се използва за вземане на решение колко растения могат да бъдат засадени.

        emptyFields = []
        try:
            for garden in self.gardens:
                emptyFields.append(garden.get_empty_fields())
        except Exception:
            self.__logBot.error(f'Could not determinate empty fields from garden {garden.getID()}.')
        return emptyFields

    def getGrowingPlantsInGardens(self):
        growingPlants = Counter()
        try:
            for garden in self.gardens:
                growingPlants.update(garden.getGrowingPlants())
        except Exception:
            self.__logBot.error('Could not determine growing plants of garden ' + str(garden.getID()) + '.')

        return dict(growingPlants)

    # Wimps
    def get_all_wimps_products(self) -> dict:
        allWimpsProducts = Counter()
        for garden in self.gardens:
            tmpWimpData = self.wimparea.get_wimps_data(garden)
            for products in tmpWimpData.values():
                allWimpsProducts.update(products[1])

        if self.aquagarden:
            tmpWimpData = self.wimparea.get_wimps_data_watergarden()
            for products in tmpWimpData.values():
                allWimpsProducts.update(products[1])

        return dict(allWimpsProducts)

    def sell_to_wimps(self, buy_from_shop: bool = False, minimal_balance: int = 500, 
        method: str = "loss", max_amount: int = 100, max_loss_in_percent: int = 33
    ):
        User().update(True)
        points_before = User().get_points()

        stock_list = Stock().get_ordered_stock_list(filter_zero=False)
        wimps_data = []
        rewards = 0
        npc_price = 0
        counter = 0

        for garden in self.gardens:
            for k, v in self.wimparea.get_wimps_data(garden).items():
                wimps_data.append({k: v})

        if self.aquagarden:
            for k, v in self.wimparea.get_wimps_data_watergarden().items():
                wimps_data.append({k: v})

        if not wimps_data:
            print("No wimps available!")
            self.__logBot.info("No wimps available!")
            return

        for wimps in wimps_data:
            for wimp, products in wimps.items():
                if not self.check_wimps_profitable(products, method, max_amount, max_loss_in_percent):
                    self.wimparea.decline(wimp)
                    self.__logBot.info(f"Declined wimp: {wimp}")
                    print(f"Declined wimp: {wimp}")
                    continue

                check, stock_list = self.check_wimps_required_amount(products[1], stock_list, minimal_balance, buy_from_shop)
                if not check:
                    continue

                rewards += products[0]
                counter += 1
                print(f"Selling products to wimp: {wimp}")
                print(self.wimparea.products_to_string(products))
                print("")
                self.__logBot.info(f"Selling products to wimp: {wimp}")
                self.wimparea.sell(wimp)
                for id, amount in products[1].items():
                    stock_list[id] -= amount
                    npc_price += ProductData().get_product_by_id(id).get_price_npc() * amount

        User().update(True)

        if counter > 0:
            points_after = User().get_points()
            points_gained = points_after - points_before

            print(f"Gained {points_gained} points.")
            print(f"Sold to {counter} wimps for {rewards:.2f} wT (equals {(rewards/npc_price):.2%} of Shop-price: {npc_price:.2f} wT)")
            self.__logBot.info(f"Gained {points_gained} points.")
            self.__logBot.info(f"Sold to {counter} wimps for {rewards:.2f} wT (equals {(rewards/npc_price):.2%} of Shop-price: {npc_price:.2f} wT)")

            sales, revenue = User().get_stats('Wimps')

            statMsg = (
                f"\n--------------------------------\n"
                f"Statistics\n"
                f"--------------------------------\n"
                f"WIMP-sales  : {sales}\n"
                f"WIMP-revenue: {revenue}\n"
                f"-------------------------------------"
            )
            print(statMsg)
            self.__logBot.info(statMsg)
        else:
            print(f"Sold to {counter} wimps")

    def check_wimps_profitable(self, products, method: str = "loss", max_amount: int = 0, max_loss_in_percent: int = 33) -> bool:
        """
        Supported methods: "all", "amount", "loss"
        """
        if method == "all":
            # Sell to all wimps no matter if it is profitable
            return True

        if method == "amount":
            # Prifitable check by Cl0ckm4n:
            # When the amount of a product <= 100, you get nearly 2/3 of the WIMP-baseprice
            for id, amount in products[1].items():
                if amount > max_amount:
                    return False
            return True

        if method == "loss":
            # Check if the price the wimp wants to pay is more then the given max loss in percent when buying every product in the shops.
            npc_sum = 0
            for id, amount in products[1].items():
                npc_sum += ProductData().get_product_by_id(id).get_price_npc() * amount
            loss = (npc_sum - products[0]) / npc_sum * 100
            # A negative loss is a profit
            if loss < 0:
                return True
            return loss <= max_loss_in_percent

        return False

    def check_wimps_required_amount(self, products, stock_list, minimal_balance, buy_from_shop: bool = False):
        for id, amount in products.items():
            product = ProductData().get_product_by_id(id)

            min_stock = minimal_balance
            if Feature().is_note_available():
                min_stock = max(self.note.get_min_stock(), self.note.get_min_stock(product.get_name()), min_stock)

            if stock_list.get(id, None) < amount + min_stock:
                if not buy_from_shop:
                    return False, stock_list

                if self.shop.buy(int(id), minimal_balance) == -1:
                    return False, stock_list
                stock_list[id] += minimal_balance

        return True, stock_list

    def getNextRunTime(self):
        garden_time = []
        for garden in self.gardens:
            garden_time.append(garden.getNextWaterHarvest())

        User().update(True)
        human_time = datetime.datetime.fromtimestamp(min(garden_time))
        print(f"Next time water/harvest: {human_time.strftime('%d/%m/%y %H:%M:%S')} ({min(garden_time)})")
        return min(garden_time)

    def hasEmptyFields(self):
        emptyFields = self.get_empty_fields()
        amount = 0
        for garden in emptyFields:
            amount += len(garden)

        return amount > 0

    def getWeedFieldsOfGardens(self):
        """Gibt alle Unkrau-Felder aller normalen Gärten zurück."""
        #BG- Връща всички полета с плевели във всички обикновени градини.
        weedFields = []
        try:
            for garden in self.gardens:
                weedFields.append(garden.getWeedFields())
        except Exception:
            self.__logBot.error(f'Could not determinate weeds on fields of garden {garden.getID()}.')

        return weedFields

    def harvest(self):
        """Harvest all gardens"""
        try:
            for garden in self.gardens:
                garden.harvest()

            if Feature().is_aqua_garden_available():
                self.aquagarden.harvest()

            Stock().update()
            self.__logBot.info(i18n.t('wimpb.harvest_successful'))
        except:
            self.__logBot.error(i18n.t('wimpb.harvest_not_successful'))

    def harvest_all_unfinished(self):
        try:
            garden: Garden
            for garden in self.gardens:
                garden.harvest_unfinished()
        except:
            raise

    def growVegetablesInGardens(self, productName, amount=-1):
        """
        Pflanzt so viele Pflanzen von einer Sorte wie möglich über alle Gärten hinweg an.
        """
        #BG-Засажда колкото е възможно повече растения от определен вид през всички градини.
        planted = 0

        product = ProductData().get_product_by_name(productName)

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

        if amount == -1 or amount > Stock().get_stock_by_product_id(product.get_id()):
            amount = Stock().get_stock_by_product_id(product.get_id())

        remainingAmount = amount
        garden: Garden
        for garden in self.gardens:
            planted += garden.grow(product.get_id(), product.get_sx(), product.get_sy(), remainingAmount)
            remainingAmount = amount - planted

        Stock().update()

        return planted

    def growPlantsInAquaGardens(self, productName, amount=-1):
        """
        Pflanzt so viele Pflanzen von einer Sorte wie möglich über alle Gärten hinweg an.
        """
        #BG-Засаждане на възможно най-много растения от определен вид през всички градини.
        if not Feature().is_aqua_garden_available():
            return

        planted = 0
        product = ProductData().get_product_by_name(productName)
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

        if amount == -1 or amount > Stock().get_stock_by_product_id(product.get_id()):
            amount = Stock().get_stock_by_product_id(product.get_id())
        remainingAmount = amount
        planted += self.aquagarden.grow(product.get_id(), product.get_sx(), product.get_sy(), product.get_edge(), remainingAmount)
        Stock().update()

        return planted

    def printStock(self, category = None):
        isSmthPrinted = False
        for productID in Stock().get_keys():
            product = ProductData().get_product_by_id(productID)

            if category is not None and product.get_category() != category:
                continue

            amount = Stock().get_stock_by_product_id(productID)
            if amount == 0: continue

            print(str(product.get_name()).ljust(30) + 'Amount: ' + str(amount).rjust(5))
            isSmthPrinted = True

        if not isSmthPrinted:
            print('Your stock is empty')

    def get_lowest_stock_entry(self, category = None):
        entryID = Stock().get_lowest_stock_entry(category)
        if entryID == -1: return 'Your stock is empty'
        return ProductData().get_product_by_id(entryID).get_name()

    def get_ordered_stock_list(self, category = None):
        orderedList = ''
        for productID in Stock().get_ordered_stock_list(category=category):
            orderedList += str(ProductData().get_product_by_id(productID).get_name()).ljust(20)
            orderedList += str(Stock().get_ordered_stock_list()[productID]).rjust(5)
            orderedList += str('\n')
        return orderedList.strip()

    def getLowestVegetableStockEntry(self):
        # Grow only plants
        if Feature().is_note_available():
            plantOnly = self.note.get_grow_only()
            if len(plantOnly) != 0:
                for productID in Stock().get_ordered_stock_list():
                    if ProductData().get_product_by_id(productID).get_name() in plantOnly:
                        return ProductData().get_product_by_id(productID).get_name()

                return 'Your stock is empty'

        # Default behaviour
        lowestStock = -1
        lowestProductId = -1
        for productID in Stock().get_ordered_stock_list():
            if not ProductData().get_product_by_id(productID).is_vegetable() or \
                not ProductData().get_product_by_id(productID).is_plantable():
                continue

            currentStock = Stock().get_stock_by_product_id(productID)
            if lowestStock == -1 or currentStock < lowestStock:
                lowestStock = currentStock
                lowestProductId = productID
                continue

        if lowestProductId == -1: return 'Your stock is empty'
        return ProductData().get_product_by_id(lowestProductId).get_name()

    def getLowestSingleVegetableStockEntry(self):
        lowestSingleStock = -1
        lowestSingleProductId = -1
        for productID in Stock().get_ordered_stock_list():
            if not ProductData().get_product_by_id(productID).is_vegetable() or \
                not ProductData().get_product_by_id(productID).is_plantable() or \
                not ProductData().get_product_by_id(productID).get_name() in ProductData().get_single_field_vegetable_list():
                continue

            currentStock = Stock().get_stock_by_product_id(productID)
            if lowestSingleStock == -1 or currentStock < lowestSingleStock:
                lowestSingleStock = currentStock
                lowestSingleProductId = productID
                continue

        if lowestSingleProductId == -1: return 'Your stock is empty'
        return ProductData().get_product_by_id(lowestSingleProductId).get_name()

    def getLowestWaterPlantStockEntry(self):
        lowestStock = -1
        lowestProductId = -1
        for productID in Stock().get_ordered_stock_list():
            if not ProductData().get_product_by_id(productID).is_water_plant() or \
                not ProductData().get_product_by_id(productID).is_plantable():
                continue

            currentStock = Stock().get_stock_by_product_id(productID)
            if lowestStock == -1 or currentStock < lowestStock:
                lowestStock = currentStock
                lowestProductId = productID
                continue

        if lowestProductId == -1: return 'Your stock is empty'
        return ProductData().get_product_by_id(lowestProductId).get_name()

    def printProductDetails(self):
        ProductData().print_all()

    def printVegetableDetails(self):
        ProductData().print_all_vegetables()

    def printWaterPlantDetails(self):
        ProductData().print_all_water_plants()

    def remove_weeds(self):
        """Removes weeds/moles/stones from all gardens"""
        #TODO: Add aqua garden
        try:
            for garden in self.gardens:
                garden.remove_weeds()
            self.__logBot.info(i18n.t('wimpb.w_harvest_successful'))
        except Exception:
            self.__logBot.error(i18n.t('wimpb.w_harvest_not_successful'))

    def get_daily_bonuses(self):
        self.bonus.get_daily_login_bonus()

        if User().is_premium_active():
            self.bonus.collect_bonus_item_points()

        if User().is_guild_member():
            self.bonus.collect_lucky_mole()

    def infinityQuest(self, MINwt):
        #TODO: Mehr Checks bzw Option wieviele Quests/WT man ausgeben mag - da es kein cooldown gibt! (hoher wt verlust)
        if User().get_bar() < MINwt:
            print('Zuwenig WT')
            pass
        if User().get_level() > 23 and User().get_bar() > MINwt:
            questnr = self.__HTTPConn.initInfinityQuest()['questnr']
            if int(questnr) <= 500:
                for item in self.__HTTPConn.initInfinityQuest()['questData']['products']:
                    #print(item)
                    product = item['pid']
                    product = ProductData().get_product_by_id(product)
                    #print(f'Pid {product.get_id()}')
                    needed = item['amount']
                    stored = Stock().get_stock_by_product_id(product.get_id())
                    #print(f'stored {stored}')
                    if needed >= stored:
                        missing = abs(needed - stored) + 10
                        #print(f'missing {missing}')
                        self.shop.buy(product.get_id(),missing)
                    try:
                        self.__HTTPConn.sendInfinityQuest(questnr, product.get_id(), needed)
                    except Exception:
                        pass

    # Bees
    def send_bees(self, tour: int):
        """@param tour: 1 = 2h, 2 = 8h, 3 = 24h"""
        if not self.honey:
            return

        honey_count = {}
        self.__update_honey_count(honey_count, self.honey.check_pour_honey())

        while self.honey.check_start_hives():
            self.honey.start_tour(tour)
            self.__update_honey_count(honey_count, self.honey.check_pour_honey())

        for key, value in honey_count.items():
            self.__logBot.info(f'Collected {value} {ProductData().get_product_by_id(key).get_name()}.')

    def __update_honey_count(self, honeycount, transfer):
        for key, value in transfer.items():
            if key in honeycount:
                honeycount[key] += value
            else:
                honeycount[key] = value

    def change_all_hives_types(self, product_name: str):
        if self.honey:
            self.honey.change_all_hives_types(ProductData().get_product_by_name(product_name).get_id())

    # Bonsai
    def cut_and_renew_bonsais(self, finish_level: int = 2, bonsai = None) -> None:
        """cut all branches and renew bonsais if lvl 2"""
        #BG-Ако нивото е 2, отрежи всички клони и поднови бонсаите.
        if self.bonsaifarm is None:
            return

        self.bonsaifarm.cutAllBonsai()
        self.bonsaifarm.checkBonsai(finish_level, bonsai)
        self.bonsaifarm.cutAllBonsai()

    # City park
    def check_park(self):
        """automate Park: first collect the cashpoint, then check if any item has to be renewed"""
        self.park.collect_cash()
        self.park.renew_all_items()

    # Herb garden
    def check_herb_garden(self):
        if not Feature().is_herb_garden_available():
            return

        self.herbgarden.remove_weeds()
        self.herbgarden.harvest()
        self.herbgarden.grow_plant()

    # Greenhouse
    def check_greenhouse(self):
        self.greenhouse.do_all_cactus_care()
