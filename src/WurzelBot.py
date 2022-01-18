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
from src.Lager import Storage
from src.Marktplatz import Marketplace
from src.Produktdaten import ProductData
import logging


class WurzelBot(object):
    """
    Die Klasse WurzelBot übernimmt jegliche Koordination aller anstehenden Aufgaben.
    """

    def __init__(self):
        """
        
        """
        self.__logBot = logging.getLogger("bot")
        self.__logBot.setLevel(logging.DEBUG)
        self.__HTTPConn = HTTPConnection()
        self.productData = ProductData(self.__HTTPConn)
        self.spieler = Spieler()
        self.messenger = Messenger(self.__HTTPConn)
        self.storage = Storage(self.__HTTPConn)
        self.garten = []
        self.wassergarten = None
        self.marktplatz = Marketplace(self.__HTTPConn)


    def __initGardens(self):
        """
        Ermittelt die Anzahl der Gärten und initialisiert alle.
        """
        try:
            tmpNumberOfGardens = self.__HTTPConn.getNumberOfGardens()
            self.spieler.numberOfGardens = tmpNumberOfGardens
            for i in range(1, tmpNumberOfGardens + 1):
                self.garten.append(Garden(self.__HTTPConn, i))
            
            if self.spieler.isAquaGardenAvailable() is True:
                self.wassergarten = AquaGarden(self.__HTTPConn)

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
        self.__logBot.debug('Error der plantSize --> sx: ' + sx + ' sy: ' + sy)


    def __getAllFieldIDsFromFieldIDAndSizeAsIntList(self, fieldID, sx, sy):
        """
        Rechnet anhand der fieldID und Größe der Pflanze (sx, sy) alle IDs aus und gibt diese als Integer-Liste zurück.
        """
        sFields = self.__getAllFieldIDsFromFieldIDAndSizeAsString(fieldID, sx, sy)
        listFields = sFields.split(',') #Stringarray
                        
        for i in range(0, len(listFields)):
            listFields[i] = int(listFields[i])
            
        return listFields


    def launchBot(self, server, user, pw):
        """
        Diese Methode startet und initialisiert den Wurzelbot. Dazu wird ein Login mit den
        übergebenen Logindaten durchgeführt und alles nötige initialisiert.
        """
        self.__logBot.info('-------------------------------------------')
        self.__logBot.info('Starte Wurzelbot')
        loginDaten = Login(server=server, user=user, password=pw)

        try:
            self.__HTTPConn.logIn(loginDaten)
        except:
            self.__logBot.error('Problem beim Starten des Wurzelbots.')
            return

        try:
            self.spieler.setUserNameFromServer(self.__HTTPConn)
        except:
            self.__logBot.error('Username konnte nicht ermittelt werden.')


        try:
            self.spieler.setUserDataFromServer(self.__HTTPConn)
        except:
            self.__logBot.error('UserDaten konnten nicht aktualisiert werden')
        
        try:
            tmpHoneyFarmAvailability = self.__HTTPConn.isHoneyFarmAvailable(self.spieler.getLevelNr())
        except:
            self.__logBot.error('Verfügbarkeit der Imkerei konnte nicht ermittelt werden.')
        else:
            self.spieler.setHoneyFarmAvailability(tmpHoneyFarmAvailability)

        try:
            tmpAquaGardenAvailability = self.__HTTPConn.isAquaGardenAvailable(self.spieler.getLevelNr())
        except:
            self.__logBot.error('Verfügbarkeit des Wassergartens konnte nicht ermittelt werden.')
        else:
            self.spieler.setAquaGardenAvailability(tmpAquaGardenAvailability)

        try:
            self.__initGardens()
        except:
            self.__logBot.error('Anzahl der Gärten konnte nicht ermittelt werden.')
 
        self.spieler.accountLogin = loginDaten
        self.spieler.setUserID(self.__HTTPConn.getUserID())
        self.productData.initAllProducts()
        self.storage.initProductList(self.productData.getListOfAllProductIDs())
        self.storage.updateNumberInStock()


    def exitBot(self):
        """
        Diese Methode beendet den Wurzelbot geordnet und setzt alles zurück.
        """
        self.__logBot.info('Beende Wurzelbot')
        try:
            self.__HTTPConn.logOut()
        except:
            self.__logBot.error('Wurzelbot konnte nicht korrekt beendet werden.')
        else:
            self.__logBot.info('Logout erfolgreich.')


    def updateUserData(self):
        """
        Ermittelt die Userdaten und setzt sie in der Spielerklasse.
        """
        try:
            userData = self.__HTTPConn.readUserDataFromServer()
        except:
            self.__logBot.error('UserDaten konnten nicht aktualisiert werden')
        else:
            self.spieler.userData = userData


    def waterPlantsInAllGardens(self):
        """
        Alle Gärten des Spielers werden komplett bewässert.
        """
        for garden in self.garten:
            garden.waterPlants()
        
        if self.spieler.isAquaGardenAvailable():
            pass
            #self.waterPlantsInAquaGarden()


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
                self.__logBot.error('Konnte keine Nachricht verschicken.')
            else:
                pass

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
            self.__logBot.error('Konnte leere Felder von Garten ' + str(garden.getID()) + ' nicht ermitteln.')
        else:
            pass
        return emptyFields

    def hasEmptyFields(self):
        emptyFields = self.getEmptyFieldsOfGardens()
        amount = 0
        for garden in emptyFields:
            amount += len(garden)

        return amount > 0

    def getWeedFieldsOfGardens(self):
        """
        Gibt alle Unkrau-Felder aller normalen Gärten zurück.
        """
        weedFields = []
        try:
            for garden in self.garten:
                weedFields.append(garden.getWeedFields())
        except:
            self.__logBot.error('Konnte Unkraut-Felder von Garten ' + str(garden.getID()) + ' nicht ermitteln.')
        else:
            pass

        return weedFields

    def harvestAllGarden(self):
        #TODO: Wassergarten ergänzen
        try:
            for garden in self.garten:
                garden.harvest()
                
            if self.spieler.isAquaGardenAvailable():
                pass#self.waterPlantsInAquaGarden()

            self.storage.updateNumberInStock()
        except:
            self.__logBot.error('Konnte nicht alle Gärten ernten.')
        else:
            self.__logBot.info('Konnte alle Gärten ernten.')
            pass


    def growPlantsInGardens(self, productName, amount=-1):
        """
        Pflanzt so viele Pflanzen von einer Sorte wie möglich über alle Gärten hinweg an.
        """
        planted = 0

        product = self.productData.getProductByName(productName)

        if product is None:
            logMsg = 'Pflanze "' + productName + '" nicht gefunden'
            self.__logBot.error(logMsg)
            print(logMsg)
            return -1

        if not self.productData.getProductByName(productName).isProductPlantable():
            logMsg = '"' + productName + '" kann nicht angepflanzt werden'
            self.__logBot.error(logMsg)
            print(logMsg)
            return -1

        if (product.isProductPlantable()):
            for garden in self.garten:
                if amount == -1 or amount > self.storage.getStockByProductID(product.getID()):
                    amount = self.storage.getStockByProductID(product.getID())
                planted += garden.growPlant(product.getID(), product.getSX(), product.getSY(), amount)
        
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
            if not self.productData.getProductByID(productID).isPlant():
                continue

            currentStock = self.storage.getStockByProductID(productID)
            if lowestStock == -1 or currentStock < lowestStock:
                lowestStock = currentStock
                lowestProductId = productID
                continue

        if lowestProductId == -1: return 'Your stock is empty'
        return self.productData.getProductByID(lowestProductId).getName()

    def printProductDetails(self):
        self.productData.printAll()
    
    def printPlantDetails(self):
        self.productData.printAllPlants()