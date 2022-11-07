#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 21.03.2017

@author: MrFlamez
'''

from src.Spieler import Spieler, Login
from src.HTTPCommunication import HTTPConnection
from src.Messenger import Messenger
from src.Garten import Garden, AquaGarden
from src.Honig import Honig
from src.Bonsai import Bonsai
from src.Lager import Storage
from src.Marktplatz import Marketplace
from src.Produktdaten import ProductData
from collections import Counter
from src.Wimps import Wimps
from src.Quests import Quest
from src.Bonus import Bonus
from src.Note import Note
from src.Shop_lists import *
import logging, i18n, datetime

i18n.load_path.append('lang')

class WurzelBot(object):
    """
    Die Klasse WurzelBot übernimmt jegliche Koordination aller anstehenden Aufgaben.
    """

    def __init__(self):
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
        self.bonus = Bonus(self.__HTTPConn, self.spieler)
        self.note = Note(self.__HTTPConn)


    def __initGardens(self):
        """Ermittelt die Anzahl der Gärten und initialisiert alle."""
        try:
            tmpNumberOfGardens = self.__HTTPConn.getInfoFromStats("Gardens")
            self.spieler.numberOfGardens = tmpNumberOfGardens
            for i in range(1, tmpNumberOfGardens + 1):
                self.garten.append(Garden(self.__HTTPConn, i))
            
            if self.spieler.isAquaGardenAvailable() is True:
                self.wassergarten = AquaGarden(self.__HTTPConn)

            if self.spieler.isHoneyFarmAvailable() is True:
                self.bienenfarm = Honig(self.__HTTPConn)

            if self.spieler.isBonsaiFarmAvailable() is True:
                self.bonsaifarm = Bonsai(self.__HTTPConn)

        except:
            raise


    def __getAllFieldIDsFromFieldIDAndSizeAsString(self, fieldID, sx, sy):
        """
        Rechnet anhand der fieldID und Größe der Pflanze (sx, sy) alle IDs aus und gibt diese als String zurück.
        """
        if (sx == '1' and sy == '1'): return str(fieldID)
        if (sx == '2' and sy == '1'): return str(fieldID) + ',' + str(fieldID + 1)
        if (sx == '1' and sy == '2'): return str(fieldID) + ',' + str(fieldID + 17)
        if (sx == '2' and sy == '2'): return str(fieldID) + ',' + str(fieldID + 1) + ',' + str(fieldID + 17) + ',' + str(fieldID + 18)
        self.__logBot.debug(f'Error der plantSize --> sx: {sx} sy: {sy}')


    def __getAllFieldIDsFromFieldIDAndSizeAsIntList(self, fieldID, sx, sy):
        """
        Rechnet anhand der fieldID und Größe der Pflanze (sx, sy) alle IDs aus und gibt diese als Integer-Liste zurück.
        """
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
        self.__logBot.info('-------------------------------------------')
        self.__logBot.info(f'Starting Wurzelbot for User {user} on Server No. {server}')
        loginDaten = Login(server=server, user=user, password=pw, language=lang)

        if portalacc == True:
            try:
                self.__HTTPConn.logInPortal(loginDaten)
            except:
                self.__logBot.error(i18n.t('wimpb.error_starting_wbot'))
                return False
        else:
            try:
                self.__HTTPConn.logIn(loginDaten)
            except:
                self.__logBot.error(i18n.t('wimpb.error_starting_wbot'))
                return False

        try:
            self.spieler.setUserNameFromServer(self.__HTTPConn)
        except:
            self.__logBot.error(i18n.t('wimpb.username_not_determined'))
            return False

        try:
            self.spieler.setUserDataFromServer(self.__HTTPConn)
        except:
            self.__logBot.error(i18n.t('wimpb.error_refresh_userdata'))
            return False
        
        try:
            self.spieler.setHoneyFarmAvailability(self.__HTTPConn.isHoneyFarmAvailable(self.spieler.getLevelNr()))
        except:
            self.__logBot.error(i18n.t('wimpb.error_no_beehives'))
            return False

        try:
            self.spieler.setAquaGardenAvailability(self.__HTTPConn.isAquaGardenAvailable(self.spieler.getLevelNr()))
        except:
            self.__logBot.error(i18n.t('wimpb.error_no_water_garden'))
            return False

        try:
            self.spieler.setBonsaiFarmAvailability(self.__HTTPConn.isBonsaiFarmAvailable(self.spieler.getLevelNr()))
        except:
            self.__logBot.error(i18n.t('wimpb.error_no_bonsaifarm'))
            return False

        try:
            self.__initGardens()
        except:
            self.__logBot.error(i18n.t('wimpb.error_number_of_gardens'))
            return False

        self.spieler.accountLogin = loginDaten
        self.spieler.setUserID(self.__HTTPConn.getUserID())
        self.productData.initAllProducts()
        self.storage.initProductList(self.productData.getListOfAllProductIDs())
        self.storage.updateNumberInStock()
        return True


    def exitBot(self):
        """Beendet den Wurzelbot geordnet und setzt alles zurück."""
        self.__logBot.info(i18n.t('wimpb.exit_wbot'))
        try:
            self.__HTTPConn.logOut()
            self.__logBot.info(i18n.t('wimpb.logout_success'))
            self.__logBot.info('-------------------------------------------')
        except:
            self.__logBot.error(i18n.t('wimpb.exit_wbot_abnormal'))


    def updateUserData(self):
        """Ermittelt die Userdaten und setzt sie in der Spielerklasse."""
        try:
            self.spieler.userData = self.__HTTPConn.readUserDataFromServer()
        except:
            self.__logBot.error(i18n.t('wimpb.error_refresh_userdata'))


    def waterPlantsInAllGardens(self):
        """Alle Gärten des Spielers werden komplett bewässert."""
        for garden in self.garten:
            garden.waterPlants()
        
        if self.spieler.isAquaGardenAvailable():
            self.wassergarten.waterPlants()


    def writeMessagesIfMailIsConfirmed(self, recipients, subject, body):
        """
        Erstellt eine neue Nachricht, füllt diese aus und verschickt sie.
        recipients muss ein Array sein!.
        Eine Nachricht kann nur verschickt werden, wenn die E-Mail Adresse bestätigt ist.
        """
        if (self.spieler.isEMailAdressConfirmed()):
            try:
                self.messenger.writeMessage(self.spieler.getUserName(), recipients, subject, body)
            except:
                self.__logBot.error(i18n.t('wimpb.no_message'))

    def getEmptyFieldsOfGardens(self):
        """
        Gibt alle leeren Felder aller normalen Gärten zurück.
        Kann dazu verwendet werden zu entscheiden, wie viele Pflanzen angebaut werden können.
        """
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

    def getAllWimpsProducts(self):
        allWimpsProducts = Counter()
        for garden in self.garten:
            tmpWimpData = self.wimparea.getWimpsData(garden)
            for products in tmpWimpData.values():
                allWimpsProducts.update(products[1])

        return dict(allWimpsProducts)

    def sellWimpsProducts(self, minimal_balance, minimal_profit):
        stock_list = self.storage.getOrderedStockList()
        wimps_data = []
        for garden in self.garten:
            for k, v in self.wimparea.getWimpsData(garden).items():
                wimps_data.append({k: v})

        for wimps in wimps_data:
            for wimp, products in wimps.items():
                if not self.checkWimpsProfitable(products, minimal_profit):
                    self.wimparea.declineWimp(wimp)
                else:
                    if self.checkWimpsRequiredAmount(minimal_balance, products[1], stock_list):
                        print("Selling products to wimp: " + wimp)
                        print(self.wimparea.productsToString(products, self.productData))
                        new_products_counts = self.wimparea.sellWimpProducts(wimp)
                        for id, amount in products[1].items():
                            stock_list[id] -= amount

    def checkWimpsProfitable(self, products, minimal_profit):
        npc_sum = 0
        for id, amount in products[1].items():
            npc_sum += self.productData.getProductByID(id).getPriceNPC() * amount
        return products[0] / npc_sum * 100 >= minimal_profit

    def checkWimpsRequiredAmount(self, minimal_balance, products, stock_list):
        to_sell = True
        for id, amount in products.items():
            product = self.productData.getProductByID(id)
            minimal_balance = max(self.note.getMinStock(), self.note.getMinStock(product.getName()), minimal_balance)
            if stock_list.get(id, 0) - (amount + minimal_balance) <= 0:
                to_sell = False
                break
        return to_sell

    def getQuestProducts(self, quest_name, quest_number=0):
        return self.quest.getQuestProducts(quest_name, quest_number)

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
        weedFields = []
        try:
            for garden in self.garten:
                weedFields.append(garden.getWeedFields())
        except:
            self.__logBot.error(f'Could not determinate weeds on fields of garden {garden.getID()}.')

        return weedFields

    def harvestAllGarden(self):
        #TODO: Wassergarten ergänzen
        try:
            for garden in self.garten:
                garden.harvest()
                
            if self.spieler.isAquaGardenAvailable():
                # TODO self.waterPlantsInAquaGarden()
                pass

            self.storage.updateNumberInStock()
            self.__logBot.info(i18n.t('wimpb.harvest_successful'))
        except:
            self.__logBot.error(i18n.t('wimpb.harvest_not_successful'))

    def growPlantsInGardens(self, productName, amount=-1):
        """
        Pflanzt so viele Pflanzen von einer Sorte wie möglich über alle Gärten hinweg an.
        """
        planted = 0

        product = self.productData.getProductByName(productName)

        if product is None:
            logMsg = f'Plant "{productName}" not found'
            self.__logBot.error(logMsg)
            print(logMsg)
            return -1

        if not product.isPlant() or not product.isPlantable():
            logMsg = f'"{productName}" could not be planted'
            self.__logBot.error(logMsg)
            print(logMsg)
            return -1

        if amount == -1 or amount > self.storage.getStockByProductID(product.getID()):
            amount = self.storage.getStockByProductID(product.getID())

        remainingAmount = amount
        garden: Garden
        for garden in self.garten:
            planted += garden.growPlant(product.getID(), product.getSX(), product.getSY(), remainingAmount)
            remainingAmount = amount - planted
        
        self.storage.updateNumberInStock()

        return planted

    def growPlantsInAquaGardens(self, productName, amount=-1):
        """
        Pflanzt so viele Pflanzen von einer Sorte wie möglich über alle Gärten hinweg an.
        """
        if self.spieler.isAquaGardenAvailable():
            planted = 0
            product = self.productData.getProductByName(productName)
            if product is None:
                logMsg = f'Plant "{productName}" not found'
                self.__logBot.error(logMsg)
                print(logMsg)
                return -1

            if not product.isPlantable():
                logMsg = f'"{productName}" could not be planted'
                self.__logBot.error(logMsg)
                print(logMsg)
                return -1

            if amount == -1 or amount > self.storage.getStockByProductID(product.getID()):
                amount = self.storage.getStockByProductID(product.getID())
            remainingAmount = amount
            planted += self.wassergarten.growPlant(product.getID(), product.getSX(), product.getSY(), remainingAmount)
            self.storage.updateNumberInStock()

            return planted

    def printStock(self):
        isSmthPrinted = False
        for productID in self.storage.getKeys():
            product = self.productData.getProductByID(productID)
            
            amount = self.storage.getStockByProductID(productID)
            if amount == 0: continue
            
            print(str(product.getName()).ljust(30) + 'Amount: ' + str(amount).rjust(5))
            isSmthPrinted = True
    
        if not isSmthPrinted:
            print('Your stock is empty')
    
    def getLowestStockEntry(self):
        entryID = self.storage.getLowestStockEntry()
        if entryID == -1: return 'Your stock is empty'
        return self.productData.getProductByID(entryID).getName()

    def getOrderedStockList(self):
        orderedList = ''
        for productID in self.storage.getOrderedStockList():
            orderedList += str(self.productData.getProductByID(productID).getName()).ljust(20)
            orderedList += str(self.storage.getOrderedStockList()[productID]).rjust(5)
            orderedList += str('\n')
        return orderedList.strip()
    
    def getLowestPlantStockEntry(self):
        lowestStock = -1
        lowestProductId = -1
        for productID in self.storage.getOrderedStockList():
            if not self.productData.getProductByID(productID).isPlant() or \
                not self.productData.getProductByID(productID).isPlantable():
                continue

            currentStock = self.storage.getStockByProductID(productID)
            if lowestStock == -1 or currentStock < lowestStock:
                lowestStock = currentStock
                lowestProductId = productID
                continue

        if lowestProductId == -1: return 'Your stock is empty'
        return self.productData.getProductByID(lowestProductId).getName()

    def getLowestSinglePlantStockEntry(self):
        lowestSingleStock = -1
        lowestSingleProductId = -1
        for productID in self.storage.getOrderedStockList():
            if not self.productData.getProductByID(productID).isPlant() or \
                not self.productData.getProductByID(productID).isPlantable() or \
                not self.productData.getProductByID(productID).getName() in self.productData.getListOfSingleFieldPlants():
                continue

            currentStock = self.storage.getStockByProductID(productID)
            if lowestSingleStock == -1 or currentStock < lowestSingleStock:
                lowestSingleStock = currentStock
                lowestSingleProductId = productID
                continue

        if lowestSingleProductId == -1: return 'Your stock is empty'
        return self.productData.getProductByID(lowestSingleProductId).getName()       

    def printProductDetails(self):
        self.productData.printAll()
    
    def printPlantDetails(self):
        self.productData.printAllPlants()

    def removeWeedInAllGardens(self):
        """Entfernt Unkraut/Maulwürfe/Steine aus allen Gärten."""
        #TODO: Wassergarten ergänzen
        try:
            for garden in self.garten:
                garden.removeWeed()
            self.__logBot.info(i18n.t('wimpb.w_harvest_successful'))
        except:
            self.__logBot.error(i18n.t('wimpb.w_harvest_not_successful'))

    def getDailyLoginBonus(self):
        self.bonus.getDailyLoginBonus()

    def infinityQuest(self, MINwt):
        #TODO: Mehr Checks bzw Option wieviele Quests/WT man ausgeben mag - da es kein cooldown gibt! (hoher wt verlust)
        if self.spieler.getBar() < MINwt:
            print('Zuwenig WT')
            pass
        if self.spieler.getLevelNr() > 23 and self.spieler.getBar() > MINwt:
            questnr = self.__HTTPConn.initInfinityQuest()['questnr']
            if int(questnr) <= 500:
                for item in self.__HTTPConn.initInfinityQuest()['questData']['products']:
                    #print(item)
                    product = item['pid']
                    product = self.productData.getProductByID(product)
                    #print(f'Pid {product.getID()}')
                    needed = item['amount']
                    stored = self.storage.getStockByProductID(product.getID())
                    #print(f'stored {stored}')
                    if needed >= stored:
                        missing = abs(needed - stored) + 10
                        #print(f'missing {missing}')
                        self.doBuyFromShop(product.getID(),missing)
                    try:
                        self.__HTTPConn.sendInfinityQuest(questnr, product.getID(), needed)
                    except:
                        pass

    # Shops
    def doBuyFromShop(self, productName, amount: int):
        if type(productName) is int:
            productName = self.productData.getProductByID(productName).getName()

        product = self.productData.getProductByName(productName)
        if product is None:
            logMsg = f'Plant "{productName}" not found'
            self.__logBot.error(logMsg)
            print(logMsg)
            return -1

        productId = product.getID()

        Shop = None
        for k, ID in Shops.items():
            if productName in k:
                Shop = ID
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
    def sendBienen(self):
        #TODO prüfen ob wirklich gesendet wurde, ansonsten Befehl wiederholen
        """
        Probiert alle Bienen für Zeitoption 1 (ohne Verkürzung 2h) zu senden
        """
        if self.spieler.isHoneyFarmAvailable():
            hives = self.__HTTPConn.getHoneyFarmInfos()[2]
            for hive in hives:
                self.__HTTPConn.sendeBienen(hive)
                self.bienenfarm.harvest()
        else:
            self.__logBot.error('Konnte nicht alle Bienen ernten.')

    # Bonsai
    def doCutBonsai(self):
        #TODO Item automatisch nach kaufen, Bonsai in den Garten setzen wenn lvl 3 erreicht
        """
        Probiert bei allen Bäumen den ersten Ast zu schneiden
        """
        sissor = None
        for key,value in self.__HTTPConn.getBonsaiFarmInfos()[3]['data']['items'].items():
            if value['item'] == "21":
                sissor = key
                print(sissor)
        if sissor is None:
            pass
        trees = self.bonsaifarm.getBonsaiAvailable()
        for tree in trees:
            self.__HTTPConn.doCutBonsai(tree, sissor)