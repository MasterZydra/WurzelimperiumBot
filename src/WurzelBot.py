#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 21.03.2017

@author: MrFlamez
'''

from collections import Counter
from src.Bonsai import Bonsai
from src.Bonus import Bonus
from src.core.Config import Config
from src.core.HTTPCommunication import HTTPConnection
from src.Garten import Garden, AquaGarden
from src.Honig import Honig
from src.Lager import Storage
from src.Marktplatz import Marketplace
from src.Messenger import Messenger
from src.note.Note import Note
from src.Produktdaten import ProductData
from src.Quests import Quest
from src.Shop_lists import *
from src.Spieler import Spieler, Login
from src.Stadtpark import Park
from src.Wimps import Wimps
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
        self.productData = ProductData(self.__HTTPConn)
        self.spieler = Spieler()
        self.messenger = Messenger(self.__HTTPConn)
        self.storage = Storage(self.__HTTPConn)
        self.garten = []
        self.wassergarten = None
        self.bienenfarm = None
        self.bonsaifarm = None
        self.marktplatz = Marketplace(self.__HTTPConn)
        self.wimparea = Wimps(self.__HTTPConn)
        self.quest = Quest(self.__HTTPConn, self.spieler)
        self.bonus = Bonus(self.__HTTPConn)
        self.note = Note()
        self.park = None


    def __initGardens(self):
        """Determines the number of gardens and initializes them."""
        try:
            # Get the number of gardens from game statistics
            tmpNumberOfGardens = self.__HTTPConn.getInfoFromStats("Gardens")
            self.spieler.numberOfGardens = tmpNumberOfGardens
            
            # Initialize regular gardens
            for i in range(1, tmpNumberOfGardens + 1):
                self.garten.append(Garden(self.__HTTPConn, i))

            # Initialize special gardens if available
            if self.spieler.isAquaGardenAvailable():
                self.wassergarten = AquaGarden(self.__HTTPConn)

            if self.spieler.isHoneyFarmAvailable():
                self.bienenfarm = Honig(self.__HTTPConn)

            if self.spieler.isBonsaiFarmAvailable():
                self.bonsaifarm = Bonsai(self.__HTTPConn)

            if self.spieler.isCityParkAvailable():
                self.park = Park(self.__HTTPConn)

        except SpecificException as e:
            raise


    def __getAllFieldIDsFromFieldIDAndSizeAsString(self, fieldID, sx, sy):
        """
        Calculates all field IDs based on the fieldID and size of the plant (sx, sy) and returns them as a string.
        """
        # Check if sx and sy are strings
        if not all(isinstance(x, str) for x in (sx, sy)):
            raise ValueError("sx and sy must be strings")

        # Convert sx and sy to integers
        sx_int, sy_int = int(sx), int(sy)

        if sx_int == 1 and sy_int == 1:
            return str(fieldID)
        elif sx_int == 2 and sy_int == 1:
            return f"{fieldID},{fieldID + 1}"
        elif sx_int == 1 and sy_int == 2:
            return f"{fieldID},{fieldID + 17}"
        elif sx_int == 2 and sy_int == 2:
            return f"{fieldID},{fieldID + 1},{fieldID + 17},{fieldID + 18}"
        else:
            raise ValueError(f"Invalid plant size: sx={sx}, sy={sy}")


    def __getAllFieldIDsFromFieldIDAndSizeAsIntList(self, fieldID, sx, sy):
        """
        Calculates all field IDs based on the fieldID and size of the plant (sx, sy) and returns them as an integer list.
        """
        # Calculate IDs as string
        sFields = self.__getAllFieldIDsFromFieldIDAndSizeAsString(fieldID, sx, sy)

        # Split string IDs and convert to integers
        try:
            listFields = [int(id) for id in sFields.split(',')]
        except ValueError:
            # Handle the case where conversion to integer fails
            raise ValueError("Invalid field IDs")

        return listFields


    def launchBot(self, server, user, pw, lang, portalacc) -> bool:
        """
        Starts and initializes the Wurzelbot by performing a login with the provided login data and initializing everything necessary.
        """
        self.__logBot.info('-------------------------------------------')
        self.__logBot.info(f'Starting Wurzelbot for User {user} on Server No. {server}')
        loginDaten = Login(server=server, user=user, password=pw, language=lang)

        try:
            if portalacc:
                self.__HTTPConn.logInPortal(loginDaten)
            else:
                self.__HTTPConn.logIn(loginDaten)

            self.spieler.setUserNameFromServer(self.__HTTPConn)
            self.spieler.setUserDataFromServer(self.__HTTPConn)
            self.spieler.setHoneyFarmAvailability(self.__HTTPConn.isHoneyFarmAvailable(self.spieler.getLevelNr()))
            self.spieler.setAquaGardenAvailability(self.__HTTPConn.isAquaGardenAvailable(self.spieler.getLevelNr()))
            self.spieler.setBonsaiFarmAvailability(self.__HTTPConn.isBonsaiFarmAvailable(self.spieler.getLevelNr()))
            self.spieler.setCityParkAvailability(self.__HTTPConn.isCityParkAvailable(self.spieler.getLevelNr()))
            self.__initGardens()
            self.spieler.accountLogin = loginDaten
            self.spieler.setUserID(self.__HTTPConn.getUserID())
            self.productData.initAllProducts()
            self.storage.initProductList(self.productData.getListOfAllProductIDs())
            self.storage.updateNumberInStock()
            return True
        except Exception as e:
            if self.__config.isDevMode:
                raise e
            if portalacc:
                self.__logBot.error("Error occurred during portal login: %s", str(e))
            else:
                self.__logBot.error("Error occurred during regular login: %s", str(e))
            return False


    def exitBot(self):
        """Gracefully shuts down the Wurzelbot and resets everything."""
        self.__logBot.info(i18n.t('wimpb.exit_wbot'))
        try:
            self.__HTTPConn.logOut()
            self.__logBot.info(i18n.t('wimpb.logout_success'))
        except Exception as e:
            self.__logBot.error("Error occurred during logout: %s", str(e))
            if self.__config.isDevMode:
                raise e
        finally:
            self.__logBot.info('-------------------------------------------')


    def updateUserData(self):
        """Fetches user data from the server and sets it in the player class."""
        try:
            self.spieler.userData = self.__HTTPConn.readUserDataFromServer()
        except Exception as e:
            self.__logBot.error("Error occurred while updating user data: %s", str(e))
            if self.__config.isDevMode:
                raise e
            else:
                self.__logBot.error(i18n.t('wimpb.error_refresh_userdata'))


    def waterPlantsInAllGardens(self):
        """Water all plants in all gardens owned by the player."""
        try:
            for garden in self.garten:
                garden.waterPlants()
                self.__logBot.info(f"All plants in Garden {garden.getID()} watered successfully.")
            
            if self.spieler.isAquaGardenAvailable():
                self.wassergarten.waterPlants()
                self.__logBot.info("All plants in Aqua Garden watered successfully.")
        except Exception as e:
            self.__logBot.error("Error occurred while watering plants: %s", str(e))
            if self.__config.isDevMode:
                raise e


    def writeMessagesIfMailIsConfirmed(self, recipients, subject, body):
        """
        Creates a new message, fills it out, and sends it.
        recipients must be an array.
        A message can only be sent if the email address is confirmed.
        """
        # Check if the email address is confirmed
        if self.spieler.isEMailAdressConfirmed():
            try:
                # Check if recipients is an array
                if isinstance(recipients, list):
                    # Create and send the message
                    self.messenger.writeMessage(self.spieler.getUserName(), recipients, subject, body)
                    self.__logBot.info("Message sent successfully.")
                else:
                    self.__logBot.error("Recipients must be an array.")
            except Exception as e:
                # Log any errors that occur during message creation and sending
                self.__logBot.error("Error occurred while creating or sending the message: %s", str(e))
                if self.__config.isDevMode:
                    raise e
        else:
            self.__logBot.error("Email address is not confirmed. Message cannot be sent.")

    def getEmptyFieldsOfGardens(self):
        """
        Retrieves all empty fields from all regular gardens.
        Can be used to decide how many plants can be planted.
        """
        emptyFields = []
        try:
            for garden in self.garten:
                empty_fields = garden.getEmptyFields()
                if empty_fields:
                    emptyFields.append(empty_fields)
        except Exception as e:
            self.__logBot.error(f'Error occurred while retrieving empty fields: {str(e)}')
        return emptyFields

    def getGrowingPlantsInGardens(self):
        """
        Retrieves all growing plants from all gardens.
        Returns a dictionary with plant IDs as keys and counts as values.
        """
        growingPlants = Counter()
        try:
            for garden in self.garten:
                plants = garden.getGrowingPlants()
                growingPlants.update(plants)
        except Exception as e:
            self.__logBot.error(f'Error occurred while retrieving growing plants: {str(e)}')

        return dict(growingPlants)

    def getAllWimpsProducts(self):
        allWimpsProducts = Counter()
        for garden in self.garten:
            tmpWimpData = self.wimparea.getWimpsData(garden)
            for wimp, products in tmpWimpData.items():
                allWimpsProducts.update(products[1])
        return dict(allWimpsProducts)

    def sellWimpsProducts(self, minimal_balance, minimal_profit):
        stock_list = self.storage.getOrderedStockList()
        for garden in self.garten:
            for wimp, products in self.wimparea.getWimpsData(garden).items():
                if self.spieler.getLevelNr() >= 3:
                    if not self.checkWimpsProfitable(products, minimal_profit):
                        self.wimparea.declineWimp(wimp)
                    else:
                        if self.checkWimpsRequiredAmount(minimal_balance, products, stock_list):
                            print("Selling products to wimp: " + wimp)
                            print(self.wimparea.products_to_string(products, self.productData))  # Corrected method name
                            new_products_counts = self.wimparea.sellWimpProducts(wimp)
                            for id, amount in products[1].items():
                                stock_list[id] -= amount

    def checkWimpsProfitable(self, products, minimal_profit_in_percent) -> bool:
        # Calculate the total price the wimp wants to pay
        wimp_total_price = sum(self.productData.getProductByID(id).getPriceNPC() * amount for id, amount in products[1].items())
        # Compare with minimal profit threshold
        return True  # Assuming it's always profitable, add logic here if needed

    def checkWimpsRequiredAmount(self, minimal_balance, products, stock_list):
        for id, amount in products[1].items():
            product = self.productData.getProductByID(id)
            min_stock = max(self.note.getMinStock(), self.note.getMinStock(product.getName()), minimal_balance)
            if stock_list.get(id, 0) < amount + min_stock or self.spieler.getLevelNr() < 3:
                return False
        return True

    def getQuestProducts(self, quest_name, quest_number=0):
        return self.quest.getQuestProducts(quest_name, quest_number)

    def getNextRunTime(self):
        garden_time = [garden.getNextWaterHarvest() for garden in self.garten]
        self.updateUserData()
        min_time = min(garden_time)
        human_time = datetime.datetime.fromtimestamp(min_time)
        print(f"Next time water/harvest: {human_time.strftime('%d/%m/%y %H:%M:%S')} ({min_time})")
        return min_time



    def hasEmptyFields(self):
        emptyFields = self.getEmptyFieldsOfGardens()
        total_empty_fields = sum(len(garden) for garden in emptyFields)
        return total_empty_fields > 0


    def getWeedFieldsOfGardens(self):
        """Returns all weed fields of all normal gardens."""
        weedFields = []
        try:
            for garden in self.garten:
                weedFields.extend(garden.getWeedFields())
        except Exception as e:
            self.__logBot.error(f'Could not determine weeds on fields of garden: {e}')
        return weedFields


    def harvestAllGarden(self):
        try:
            for garden in self.garten:
                garden.harvest()
            
            if self.spieler.isAquaGardenAvailable():
                self.wassergarten.harvest()

            self.storage.updateNumberInStock()
            self.__logBot.info(i18n.t('wimpb.harvest_successful'))
        except Exception as e:
            self.__logBot.error(i18n.t('wimpb.harvest_not_successful') + str(e))


    def growVegetablesInGardens(self, productName, amount=-1):
        """
        Plant as many plants of a certain type as possible across all gardens.
        """
        planted = 0
        product = self.productData.getProductByName(productName)
        if product is None:
            logMsg = f'Plant "{productName}" not found'
            self.__logBot.error(logMsg)
            print(logMsg)
            return -1

        if not product.isVegetable() or not product.isPlantable():
            logMsg = f'"{productName}" could not be planted'
            self.__logBot.error(logMsg)
            print(logMsg)
            return -1

        if amount == -1 or amount > self.storage.getStockByProductID(product.getID()):
            amount = self.storage.getStockByProductID(product.getID())

        remainingAmount = amount
        for garden in self.garten:
            planted += garden.growPlant(product.getID(), product.getSX(), product.getSY(), remainingAmount)
            remainingAmount = amount - planted

        self.storage.updateNumberInStock()
        return planted

    def growPlantsInAquaGardens(self, productName, amount=-1):
        """
        Plant as many plants of a certain type as possible across all aqua gardens.
        """
        if not self.spieler.isAquaGardenAvailable():
            return -1

        planted = 0
        product = self.productData.getProductByName(productName)
        if product is None:
            logMsg = f'Plant "{productName}" not found'
            self.__logBot.error(logMsg)
            print(logMsg)
            return -1

        if not product.isWaterPlant() or not product.isPlantable():
            logMsg = f'"{productName}" could not be planted'
            self.__logBot.error(logMsg)
            print(logMsg)
            return -1

        if amount == -1 or amount > self.storage.getStockByProductID(product.getID()):
            amount = self.storage.getStockByProductID(product.getID())

        remainingAmount = amount
        planted += self.wassergarten.growPlant(product.getID(), product.getSX(), product.getSY(), product.getEdge(), remainingAmount)
        self.storage.updateNumberInStock()

        return planted


    def printStock(self):
        isSmthPrinted = False
        for productID in self.storage.getKeys():
            product = self.productData.getProductByID(productID)
            amount = self.storage.getStockByProductID(productID)
            if amount != 0:
                print(f'{product.getName():<30} Amount: {amount:>5}')
                isSmthPrinted = True

        if not isSmthPrinted:
            print('Your stock is empty')


    def getLowestStockEntry(self):
        entryID = self.storage.getLowestStockEntry()
        if entryID == -1:
            return 'Your stock is empty'
        return self.productData.getProductByID(entryID).getName()


    def getOrderedStockList(self):
        orderedList = ''
        for productID in self.storage.getOrderedStockList():
            product = self.productData.getProductByID(productID)
            amount = self.storage.getOrderedStockList()[productID]
            orderedList += f'{product.getName():<20}{amount:>5}\n'
        return orderedList.strip()


    def getLowestVegetableStockEntry(self):
        lowestStock = float('inf')
        lowestProductId = -1
        for productID in self.storage.getOrderedStockList():
            product = self.productData.getProductByID(productID)
            if product.isVegetable() and product.isPlantable():
                currentStock = self.storage.getStockByProductID(productID)
                if currentStock < lowestStock:
                    lowestStock = currentStock
                    lowestProductId = productID

        if lowestProductId == -1:
            return 'Your stock is empty'
        return self.productData.getProductByID(lowestProductId).getName()


    def getLowestSingleVegetableStockEntry(self):
        lowestSingleStock = float('inf')
        lowestSingleProductId = -1
        for productID in self.storage.getOrderedStockList():
            product = self.productData.getProductByID(productID)
            if product.isVegetable() and product.isPlantable() and product.getName() in self.productData.getListOfSingleFieldVegetables():
                currentStock = self.storage.getStockByProductID(productID)
                if currentStock < lowestSingleStock:
                    lowestSingleStock = currentStock
                    lowestSingleProductId = productID

        if lowestSingleProductId == -1:
            return 'Your stock is empty'
        return self.productData.getProductByID(lowestSingleProductId).getName()


    def getLowestWaterPlantStockEntry(self):
        lowestStock = float('inf')
        lowestProductId = -1
        for productID in self.storage.getOrderedStockList():
            product = self.productData.getProductByID(productID)
            if product.isWaterPlant() and product.isPlantable():
                currentStock = self.storage.getStockByProductID(productID)
                if currentStock < lowestStock:
                    lowestStock = currentStock
                    lowestProductId = productID

        if lowestProductId == -1:
            return 'Your stock is empty'
        return self.productData.getProductByID(lowestProductId).getName()


    def printProductDetails(self):
        self.productData.printAll()

    def printVegetableDetails(self):
        self.productData.printAllVegetables()

    def printWaterPlantDetails(self):
        self.productData.printAllWaterPlants()

    def removeWeedInAllGardens(self):
        """Removes weeds/moles/stones from all gardens."""
        try:
            for garden in self.garten:
                garden.removeWeed()
            self.__logBot.info(i18n.t('wimpb.w_harvest_successful'))
        except Exception as e:
            self.__logBot.error(i18n.t('wimpb.w_harvest_not_successful') + str(e))


    def getDailyLoginBonus(self):
        self.bonus.getDailyLoginBonus()

    def infinityQuest(self, MINwt):
        if self.spieler.getBar() < MINwt:
            print('Not enough WT')
            return

        if self.spieler.getLevelNr() > 23 and self.spieler.getBar() > MINwt:
            quest_data = self.__HTTPConn.initInfinityQuest()
            questnr = quest_data.get('questnr')
            if questnr and int(questnr) <= 500:
                for item in quest_data.get('questData', {}).get('products', []):
                    product_id = item.get('pid')
                    product = self.productData.getProductByID(product_id)
                    needed = item.get('amount')
                    stored = self.storage.getStockByProductID(product_id)
                    if needed >= stored:
                        missing = abs(needed - stored) + 10
                        self.doBuyFromShop(product_id, missing)
                    try:
                        self.__HTTPConn.sendInfinityQuest(questnr, product_id, needed)
                    except Exception as e:
                        pass

    def doBuyFromShop(self, productName, amount: int):
        if isinstance(productName, int):
            product = self.productData.getProductByID(productName)
            if product is None:
                logMsg = f'Product with ID "{productName}" not found'
                self.__logBot.error(logMsg)
                print(logMsg)
                return -1
        else:
            product = self.productData.getProductByName(productName)
            if product is None:
                logMsg = f'Product "{productName}" not found'
                self.__logBot.error(logMsg)
                print(logMsg)
                return -1

        Shop = None
        for k, ID in Shops.items():
            if productName in k:
                Shop = ID
                break

        if Shop in [1, 2, 3, 4]:
            try:
                self.__HTTPConn.buyFromShop(Shop, product.getID(), amount)
            except Exception as e:
                pass
        elif Shop == 0:
            try:
                self.__HTTPConn.buyFromAquaShop(product.getID(), amount)
            except Exception as e:
                pass
        return 0


    def sendBienen(self):
        """
        Attempts to send all bees for time option 1 (without reduction 2h).
        """
        if self.spieler.isHoneyFarmAvailable():
            hives = self.__HTTPConn.getHoneyFarmInfos()[2]
            for hive in hives:
                try:
                    self.__HTTPConn.sendeBienen(hive)
                    self.bienenfarm.harvest()
                except Exception as e:
                    logMsg = f'Error sending bees: {e}'
                    print(logMsg)
                    self.__logBot.error(logMsg)
        else:
            logMsg = 'Could not harvest all bees.'
            print(logMsg)
            self.__logBot.error(logMsg)

    # Bonsai
    def cutAndRenewBonsais(self):
        """cut all branches and renew bonsais if lvl 2"""
        #BG-Ако нивото е 2, отрежи всички клони и поднови бонсаите.
        self.bonsaifarm.cutAllBonsai()
        self.bonsaifarm.checkBonsai()
        self.bonsaifarm.cutAllBonsai()

    # Stadtpark
    def checkPark(self):
        """automate Park: first collect the cashpoint, then check if any item has to be renewed"""
        self.park.collectCashFromCashpoint()
        self.park.renewAllItemsInPark()
