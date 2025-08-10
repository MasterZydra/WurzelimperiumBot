#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 21.03.2017

@author: MrFlamez
'''

from src.bonsai.Bonsai import Bonsai
from src.bonus.Bonus import Bonus
from src.citypark.CityPark import CityPark
from src.core.Feature import Feature
from src.core.HTTPCommunication import HTTPConnection
from src.core.Login import Login
from src.core.User import User
from src.garden.aqua.AquaGarden import AquaGarden
from src.garden.Garden import Garden
from src.garden.herb.HerbGarden import HerbGarden
from src.greenhouse.Greenhouse import Greenhouse
from src.honey.Honey import Honey
from src.logger.Logger import Logger
from src.marketplace.Marketplace import Marketplace
from src.megafruit.Megafruit import Megafruit
from src.megafruit.MegafruitData import Mushroom, Care_OID
from src.message.Messenger import Messenger
from src.minigames.Minigames import Minigames
from src.note.Note import Note
from src.product.ProductData import ProductData
from src.quest.Quest import Quest
from src.shop.Shop import Shop
from src.stock.Stock import Stock
from src.wimp.Wimp import Wimp
from collections import Counter
import i18n, datetime

i18n.load_path.append('lang')

class WurzelBot:
    """
    Die Klasse WurzelBot übernimmt jegliche Koordination aller anstehenden Aufgaben.
    """
    #BG- """ Класът WurzelBot се грижи за координацията на всички предстоящи задачи."""


    def __init__(self):
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
        self.megafruit = None
        self.minigames = Minigames()


    def __init_gardens(self) -> bool:
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

            if Feature().is_megafruit_available():
                self.megafruit = Megafruit()

            return True

        except Exception:
            Logger().print_exception('Failed to init gardens')
            return False


    def login(self, server, user, pw, lang, portalacc) -> bool:
        """
        Diese Methode startet und initialisiert den Wurzelbot. Dazu wird ein Login mit den
        übergebenen Logindaten durchgeführt und alles nötige initialisiert.
        """
        #BG-Този метод стартира и инициализира Wurzelbot. За целта се извършва вход с предоставените данни за влизане и се инициализира всичко необходимо.

        Logger().debug(f'Starting Wurzelbot for User {user} on Server No. {server}')
        loginDaten = Login(server=server, user=user, password=pw, language=lang)

        if portalacc == True:
            if not self.__HTTPConn.logInPortal(loginDaten):
                return False
        else:
            if not self.__HTTPConn.logIn(loginDaten):
                return False

        if not User().update():
            return False

        if not self.__init_gardens():
            return False

        User().accountLogin = loginDaten

        if not ProductData().init():
            return False

        Stock().init_product_list(ProductData().get_product_id_list())
        return Stock().update()


    def logout(self):
        """Exit the bot cleanly with login and reset the data"""
        Logger().print(i18n.t('wimpb.exit_wbot'))

        if self.__HTTPConn.logOut():
            Logger().print(i18n.t('wimpb.logout_success'))

    def get_stop_bot_note(self) -> bool:
        """Check notes for stop bot entry"""
        if self.note is None:
            return False

        return self.note.get_stop_bot()

    def water(self) -> bool:
        """Waters all of the player's gardens"""
        garden: Garden
        for garden in self.gardens:
            if not garden.water():
                return False

        if self.aquagarden is not None:
            if not self.aquagarden.water():
                return False

        return True

    def writeMessageIfMailIsConfirmed(self, recipients, subject, body):
        """
        Erstellt eine neue Nachricht, füllt diese aus und verschickt sie.
        recipients muss ein Array sein!.
        Eine Nachricht kann nur verschickt werden, wenn die E-Mail Adresse bestätigt ist.
        """
        #BG-Създава ново съобщение, попълва го и го изпраща.Получателите трябва да са в масив! Съобщение може да бъде изпратено само ако електронната поща е потвърдена.

        if User().is_mail_confirmed():
            if not self.messenger.write(recipients, subject, body):
                Logger().print_error(i18n.t('wimpb.no_message'))

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
            Logger().print_error(f'Could not determinate empty fields from garden {garden.getID()}.')
        return emptyFields

    def getGrowingPlantsInGardens(self):
        growingPlants = Counter()
        try:
            for garden in self.gardens:
                growingPlants.update(garden.getGrowingPlants())
        except Exception:
            Logger().print_error('Could not determine growing plants of garden ' + str(garden.getID()) + '.')

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
    ) -> bool:
        if not User().update(True):
            return False
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
            Logger().print("No wimps available!")
            return False

        for wimps in wimps_data:
            for wimp, products in wimps.items():
                if not self.check_wimps_profitable(products, method, max_amount, max_loss_in_percent):
                    self.wimparea.decline(wimp)
                    Logger().print(f"Declined wimp: {wimp}")
                    continue

                check, stock_list = self.check_wimps_required_amount(products[1], stock_list, minimal_balance, buy_from_shop)
                if not check:
                    continue

                rewards += products[0]
                counter += 1
                Logger().print(f"Selling products to wimp: {wimp}")
                Logger().print(self.wimparea.products_to_string(products))
                print("")
                self.wimparea.sell(wimp)
                for id, amount in products[1].items():
                    stock_list[id] -= amount
                    npc_price += ProductData().get_product_by_id(id).get_price_npc() * amount

        if not User().update(True):
            return False

        if counter > 0:
            points_after = User().get_points()
            points_gained = points_after - points_before

            Logger().print(f"Gained {points_gained} points.")
            Logger().print(f"Sold to {counter} wimps for {rewards:.2f} wT (equals {(rewards/npc_price):.2%} of Shop-price: {npc_price:.2f} wT)")

            sales, revenue = User().get_stats('Wimps')

            Logger().print(
                f"\n--------------------------------\n"
                f"Statistics\n"
                f"--------------------------------\n"
                f"WIMP-sales  : {sales}\n"
                f"WIMP-revenue: {revenue}\n"
                f"-------------------------------------"
            )
        else:
            Logger().print(f"Sold to {counter} wimps")

        return True

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
            if self.note is not None:
                min_stock = max(self.note.get_min_stock(), self.note.get_min_stock(product.get_name()), min_stock)

            if stock_list.get(id, None) < amount + min_stock:
                if not buy_from_shop:
                    return False, stock_list

                if self.shop.buy(int(id), minimal_balance):
                    return False, stock_list
                stock_list[id] += minimal_balance

        return True, stock_list

    def getNextRunTime(self):
        garden_time = []
        garden: Garden
        for garden in self.gardens:
            garden_time.append(garden.getNextWaterHarvest())

        if not User().update(True):
            return None

        human_time = datetime.datetime.fromtimestamp(min(garden_time))
        Logger().print(f"Next time water/harvest: {human_time.strftime('%d/%m/%y %H:%M:%S')} ({min(garden_time)})")
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
                weedFields.append(garden.get_weed_fields())
        except Exception:
            Logger().print_error(f'Could not determinate weeds on fields of garden {garden.getID()}.')

        return weedFields

    def harvest(self) -> bool:
        """Harvest all gardens"""
        garden: Garden
        for garden in self.gardens:
            if not garden.harvest():
                return False

        if self.aquagarden is not None:
            if not self.aquagarden.harvest():
                return False

        Logger().print(i18n.t('wimpb.harvest_successful'))
        return Stock().update()

    def harvest_all_unfinished(self) -> bool:
        garden: Garden
        for garden in self.gardens:
            if not garden.harvest_unfinished():
                return False
        return True

    def growVegetablesInGardens(self, productName, amount=-1):
        """
        Pflanzt so viele Pflanzen von einer Sorte wie möglich über alle Gärten hinweg an.
        """
        #BG-Засажда колкото е възможно повече растения от определен вид през всички градини.
        planted = 0

        product = ProductData().get_product_by_name(productName)

        if product is None:
            Logger().print_error(f'Plant "{productName}" not found')
            return None

        if not product.is_vegetable() or not product.is_plantable():
            Logger().print_error(f'"{productName}" could not be planted')
            return None

        if amount == -1 or amount > Stock().get_stock_by_product_id(product.get_id()):
            amount = Stock().get_stock_by_product_id(product.get_id())

        remainingAmount = amount
        garden: Garden
        for garden in self.gardens:
            lastPlanted = garden.grow(product.get_id(), product.get_sx(), product.get_sy(), remainingAmount)
            if lastPlanted is None:
                return None
            planted += lastPlanted
            remainingAmount = amount - planted

        if not Stock().update():
            return None

        return planted

    def growPlantsInAquaGardens(self, productName, amount=-1):
        """
        Pflanzt so viele Pflanzen von einer Sorte wie möglich über alle Gärten hinweg an.
        """
        #BG-Засаждане на възможно най-много растения от определен вид през всички градини.
        if self.aquagarden is None:
            return 0

        planted = 0
        product = ProductData().get_product_by_name(productName)
        if product is None:
            Logger().print_error(f'Plant "{productName}" not found')
            return None

        if not product.is_water_plant() or not product.is_plantable():
            Logger().print_error(f'"{productName}" could not be planted')
            return None

        if amount == -1 or amount > Stock().get_stock_by_product_id(product.get_id()):
            amount = Stock().get_stock_by_product_id(product.get_id())
        remainingAmount = amount
        lastPlanted = self.aquagarden.grow(product.get_id(), product.get_sx(), product.get_sy(), product.get_edge(), remainingAmount)
        if lastPlanted is None:
            return None
        planted += lastPlanted
        if not Stock().update():
            return None

        return planted

    def printStock(self, category = None):
        isSmthPrinted = False
        for productID in Stock().get_keys():
            product = ProductData().get_product_by_id(productID)

            if category is not None and product.get_category() != category:
                continue

            amount = Stock().get_stock_by_product_id(productID)
            if amount == 0: continue

            Logger().print(str(product.get_name()).ljust(30) + 'Amount: ' + str(amount).rjust(5))
            isSmthPrinted = True

        if not isSmthPrinted:
            Logger().print('Your stock is empty')

    def get_lowest_stock_entry(self):
        entryID = Stock().get_lowest_stock_entry()
        if entryID == -1: return 'Your stock is empty'
        return ProductData().get_product_by_id(entryID).get_name()

    def get_ordered_stock_list(self):
        orderedList = ''
        for productID in Stock().get_ordered_stock_list():
            orderedList += str(ProductData().get_product_by_id(productID).get_name()).ljust(20)
            orderedList += str(Stock().get_ordered_stock_list()[productID]).rjust(5)
            orderedList += str('\n')
        return orderedList.strip()

    def getLowestVegetableStockEntry(self):
        # Grow only plants
        if self.note is not None:
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

    def remove_weeds(self) -> bool:
        """Removes weeds/moles/stones from all gardens"""
        #TODO: Add aqua garden
        garden: Garden
        for garden in self.gardens:
            if not garden.remove_weeds():
                Logger().print_error(i18n.t('wimpb.w_harvest_not_successful'))
                return False
        Logger().print(i18n.t('wimpb.w_harvest_successful'))

    def get_daily_bonuses(self) -> bool:
        self.bonus.get_daily_login_bonus()

        if User().is_premium_active():
            self.bonus.collect_bonus_item_points()

        if User().is_guild_member():
            if not self.bonus.collect_lucky_mole():
                return False

        return True

    def infinityQuest(self, MINwt):
        #TODO: Mehr Checks bzw Option wieviele Quests/WT man ausgeben mag - da es kein cooldown gibt! (hoher wt verlust)
        if User().get_bar() < MINwt:
            Logger().print('Zu wenig WT')
            return

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

                    self.__HTTPConn.sendInfinityQuest(questnr, product.get_id(), needed)

    # Bees
    def send_bees(self, tour: int) -> bool:
        """@param tour: 1 = 2h, 2 = 8h, 3 = 24h"""
        if not self.honey:
            return

        honey_count = {}
        if not self.__update_honey_count(honey_count, self.honey.check_pour_honey()):
            return False

        while self.honey.check_start_hives():
            if not self.honey.start_tour(tour):
                return False
            if not self.__update_honey_count(honey_count, self.honey.check_pour_honey()):
                return False

        for key, value in honey_count.items():
            Logger().print(f'Collected {value} {ProductData().get_product_by_id(key).get_name()}.')

        return True

    def __update_honey_count(self, honey_count, transfer) -> bool:
        if transfer is None:
            return False
        for key, value in transfer.items():
            if key in honey_count:
                honey_count[key] += value
            else:
                honey_count[key] = value
        return True

    def change_all_hives_types(self, product_name: str) -> bool:
        if not self.honey:
            return False
        return self.honey.change_all_hives_types(ProductData().get_product_by_name(product_name).get_id())

    # Bonsai
    def cut_and_renew_bonsais(self, finish_level: int = 2, bonsai = None, allowed_prices: list = ['money', 'coins']):
        """
        cut all branches and renew bonsais if lvl 2
        allowed_prices: All allowed values: ['money', 'coins']
        """
        #BG-Ако нивото е 2, отрежи всички клони и поднови бонсаите.
        if self.bonsaifarm is None:
            return

        self.bonsaifarm.cut_all()
        self.bonsaifarm.check(finish_level, bonsai, allowed_prices)
        self.bonsaifarm.cut_all()

    # City park
    def check_park(self) -> bool:
        """automate Park: first collect the cashpoint, then check if any item has to be renewed"""
        if not self.park.collect_cash():
            return False
        return self.park.renew_all_items()

    # Herb garden
    def check_herb_garden(self) -> bool:
        if self.herbgarden is None:
            return False
        if not self.herbgarden.remove_weeds():
            return False
        if not self.herbgarden.harvest():
            return False
        if self.herbgarden.grow_plant() is None:
            return False
        return True

    # Greenhouse
    def check_greenhouse(self) -> bool:
        if self.greenhouse is None:
            return False

        return self.greenhouse.do_all_cactus_care()

    # Megafruit
    def check_megafruit(self, mushroom: Mushroom = Mushroom.MUSHROOM, buy_from_shop: bool = False, allowed_care_item_prices: list = ['money', 'fruits']) -> bool:
        """
        allowed_care_item_prices: All allowed values: ['money', 'coins', 'fruits']
        """
        if self.megafruit is None:
            return False

        if not self.megafruit.finish():
            return False

        # Only check for stock if not plant is growing
        if self.megafruit.is_planted() and self.megafruit.get_remaining_time() > 0:
            stock_list = Stock().get_ordered_stock_list(False)
            id = mushroom.value
            # TODO: adjust for different mushrooms / check Sporen for Goldener Flauschling
            min_stock = 1800
            if stock_list.get(str(id), 0) < min_stock:
                if not buy_from_shop:
                    return False

                if self.buy_from_shop(int(id), min_stock) == -1:
                    return False

            if not self.megafruit.start(mushroom):
                return False

        # Get best care item for each type and apply it
        for type in ['water', 'light', 'fertilize']:
            best_item = self.megafruit.get_best_care_item(type, allowed_care_item_prices)
            if best_item is None:
                continue

            if not self.megafruit.care(best_item):
                return False

        return self.megafruit.finish()
