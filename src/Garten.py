#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import Counter, namedtuple
import logging, i18n
from src.HTTPCommunication import HTTPConnection
from src.WurzelBot import WurzelBot

i18n.load_path.append('lang')

class Garden():
    _LEN_X = 17
    _LEN_Y = 12
    _MAX_FIELDS = _LEN_X * _LEN_Y
    
    def __init__(self, httpConnection: HTTPConnection, gardenID):
        self._httpConn = httpConnection
        self._id = gardenID
        self._logGarden = logging.getLogger('bot.Garden_' + str(gardenID))
        self._logGarden.setLevel(logging.DEBUG)

    def _getAllFieldIDsFromFieldIDAndSizeAsString(self, fieldID, sx, sy):
        """
        Rechnet anhand der fieldID und Größe der Pflanze (sx, sy) alle IDs aus und gibt diese als String zurück.
        """
        
        # Field indices (x) returned for plants of size 1, 2, and 4 fields.
        # Important when watering; all indices must be specified there.
        # (Both those marked with x and those marked with o).
        # x: fieldID
        # o: added fields based on the size
        # +---+   +---+---+   +---+---+
        # | x |   | x | o |   | x | o |
        # +---+   +---+---+   +---+---+
        #                     | o | o |
        #                     +---+---+
        
        if (sx == 1 and sy == 1): return str(fieldID)
        if (sx == 2 and sy == 1): return str(fieldID) + ',' + str(fieldID + 1)
        if (sx == 1 and sy == 2): return str(fieldID) + ',' + str(fieldID + 17)
        if (sx == 2 and sy == 2): return str(fieldID) + ',' + str(fieldID + 1) + ',' + str(fieldID + 17) + ',' + str(fieldID + 18)
        self._logGarden.debug(f'Error der plantSize --> sx: {sx} sy: {sy}')

    def _getAllFieldIDsFromFieldIDAndSizeAsIntList(self, fieldID, sx, sy):
        """
        Calculates all IDs based on the fieldID and size of the plant (sx, sy) and returns them as an integer list.
        """
        sFields = self._getAllFieldIDsFromFieldIDAndSizeAsString(fieldID, sx, sy)
        listFields = sFields.split(',') #Stringarray
                        
        for i in range(0, len(listFields)):
            listFields[i] = int(listFields[i])
            
        return listFields
    
    def _isPlantGrowableOnField(self, fieldID, emptyFields, fieldsToPlant, sx):
        """Prüft anhand mehrerer Kriterien, ob ein Anpflanzen möglich ist."""
        # Betrachtetes Feld darf nicht besetzt sein
        if not (fieldID in emptyFields): return False
        
        # Anpflanzen darf nicht außerhalb des Gartens erfolgen
        # Dabei reicht die Betrachtung in x-Richtung, da hier ein
        # "Zeilenumbruch" stattfindet. Die y-Richtung ist durch die
        # Abfrage abgedeckt, ob alle benötigten Felder frei sind.
        # Felder außerhalb (in y-Richtung) des Gartens sind nicht leer,
        # da sie nicht existieren.
        if not ((self._MAX_FIELDS - fieldID)%self._LEN_X >= sx - 1): return False
        fieldsToPlantSet = set(fieldsToPlant)
        emptyFieldsSet = set(emptyFields)
        
        # Alle benötigten Felder der Pflanze müssen leer sein
        if not (fieldsToPlantSet.issubset(emptyFieldsSet)): return False
        return True

    def getID(self):
        """Returns the ID of garden."""
        return self._id

    def waterPlants(self):
        """Ein Garten mit der gardenID wird komplett bewässert."""
        self._logGarden.info(f'Gieße alle Pflanzen im Garten {self._id}.')
        try:
            plants = self._httpConn.getPlantsToWaterInGarden(self._id)
            nPlants = len(plants['fieldID'])
            for i in range(0, nPlants):
                sFields = self._getAllFieldIDsFromFieldIDAndSizeAsString(plants['fieldID'][i], plants['sx'][i], plants['sy'][i])
                self._httpConn.waterPlantInGarden(self._id, plants['fieldID'][i], sFields)
        except:
            self._logGarden.error(f'Garten {self._id} konnte nicht bewässert werden.')
        else:
            self._logGarden.info(f'Im Garten {self._id} wurden {nPlants} Pflanzen gegossen.')
            print(f'Im Garten {self._id} wurden {nPlants} Pflanzen gegossen.')

    def getEmptyFields(self):
        """Returns all empty fields in the garden."""
        try:
            return self._httpConn.getEmptyFieldsOfGarden(self._id)
        except:
            self._logGarden.error(f'Konnte leere Felder von Garten {self._id} nicht ermitteln.')

    def getWeedFields(self):
        """Returns all weed fields in the garden."""
        try:
            return self._httpConn.getWeedFieldsOfGarden(self._id)
        except:
            self._logGarden.error(f'Konnte Unkraut-Felder von Garten {self._id} nicht ermitteln.')

    def getGrowingPlants(self):
        """Returns all growing plants in the garden."""
        try:
            return Counter(self._httpConn.getGrowingPlantsOfGarden(self._id))
        except:
            self._logGarden.error('Could not determine growing plants of garden ' + str(self._id) + '.')

    def getNextWaterHarvest(self):
        """Returns all growing plants in the garden."""
        overall_time = []
        Fields_data = namedtuple("Fields_data", "plant water harvest")
        max_water_time = 86400
        try:
            garden = self._httpConn._changeGarden(self._id).get('garden')
            for field in garden.values():
                if field[0] in [41, 42, 43, 45]:
                    continue
                fields_time = Fields_data(field[10], field[4], field[3])
                if fields_time.harvest - fields_time.water > max_water_time:
                    overall_time.append(fields_time.water + max_water_time)
                overall_time.append(fields_time.harvest)
            return min(overall_time)
        except:
            self._logGarden.error('Could not determine growing plants of garden ' + str(self._id) + '.')

    def harvest(self):
        """Harvest everything"""
        try:
            self._httpConn.harvestGarden(self._id)
        except:
            raise

    def growPlant(self, plantID, sx, sy, amount):
        """Grows a plant of any size."""
        planted = 0
        emptyFields = self.getEmptyFields()
        
        try:
            for field in range(1, self._MAX_FIELDS + 1):
                if planted == amount: break

                fieldsToPlant = self._getAllFieldIDsFromFieldIDAndSizeAsIntList(field, sx, sy)
                
                if (self._isPlantGrowableOnField(field, emptyFields, fieldsToPlant, sx)):
                    fields = self._getAllFieldIDsFromFieldIDAndSizeAsString(field, sx, sy)
                    self._httpConn.growPlant(field, plantID, self._id, fields)
                    planted += 1

                    #Nach dem Anbau belegte Felder aus der Liste der leeren Felder loeschen
                    fieldsToPlantSet = set(fieldsToPlant)
                    emptyFieldsSet = set(emptyFields)
                    tmpSet = emptyFieldsSet - fieldsToPlantSet
                    emptyFields = list(tmpSet)

        except:
            self._logGarden.error(f'Im Garten {self._id} konnte nicht gepflanzt werden.')
            return 0
        else:
            msg = f'Im Garten {self._id} wurden {planted} Pflanzen gepflanzt.'
            if emptyFields: 
                msg = msg + f' Im Garten {self._id} sind noch leere Felder vorhanden.'
            self._logGarden.info(msg)
            print(msg)
            return planted

    def removeWeed(self):
        """
        Entfernt alles Unkraut, Steine und Maulwürfe, wenn ausreichend Geld vorhanden ist.
        """
        weedFields = self.getWeedFields()
        freeFields = []
        for fieldID in weedFields:
            try:
                result = self._httpConn.removeWeedOnFieldInGarden(self._id, fieldID)
            except:
                self._logGarden.error(f'Feld {fieldID} im Garten {self._id} konnte nicht von Unkraut befreit werden!')
            else:
                if result == 1:
                    self._logGarden.info(f'Feld {fieldID} im Garten {self._id} wurde von Unkraut befreit!')
                    freeFields.append(fieldID)
                else:
                    self._logGarden.error(f'Feld {fieldID} im Garten {self._id} konnte nicht von Unkraut befreit werden!')

        self._logGarden.info(f'Im Garten {self._id} wurden {len(freeFields)} Felder von Unkraut befreit.')


class AquaGarden(Garden):   
    def __init__(self, httpConnection):
        Garden.__init__(self, httpConnection, 101)
        self.__setInnerFields()
        self.__setOuterFields()

    def __setInnerFields(self, distance=2):
        """defines the fieldID's of the inner watergarden planting area"""
        self._INNER_FIELDS = []
        for i in range(distance, self._LEN_Y-distance):
            self._INNER_FIELDS.extend(range(i * self._LEN_X + distance + 1, (i + 1) * self._LEN_X - distance + 1))

    def __setOuterFields(self):
        """defines the fieldID's of the outer watergarden planting area"""
        temp_fields = list(range(1, self._MAX_FIELDS+1))
        self._OUTER_FIELDS = [x for x in temp_fields if x not in self._INNER_FIELDS]
        
    def _isPlantGrowableOnField(self, fieldID, emptyFields, fieldsToPlant, edge):
        """Prüft anhand mehrerer Kriterien, ob ein Anpflanzen möglich ist."""
        # Betrachtetes Feld darf nicht besetzt sein
        if not (fieldID in emptyFields): return False

        #Randpflanze im Wassergarten
        if edge == 1:
            if not [x for x in fieldsToPlant if x in self._OUTER_FIELDS] == fieldsToPlant: return False

        #Wasserpflanzen im Wassergarten
        if edge == 0:
            if not [x for x in fieldsToPlant if x in self._INNER_FIELDS] == fieldsToPlant: return False
    
        fieldsToPlantSet = set(fieldsToPlant)
        emptyFieldsSet = set(emptyFields)
        
        # Alle benötigten Felder der Pflanze müssen leer sein
        if not (fieldsToPlantSet.issubset(emptyFieldsSet)): return False
        return True

    def getEmptyAquaFields(self):
        """
        Gibt alle leeren Felder des Gartens zurück.
        """
        try:
            tmpEmptyAquaFields = self._httpConn.getEmptyFieldsAqua()
        except:
            self._logGarden.error('Konnte leere Felder von AquaGarten nicht ermitteln.')
        else:
            return tmpEmptyAquaFields

    def waterPlants(self):
        """
        Alle Pflanzen im Wassergarten werden bewässert.
        """
        try:
            plants = self._httpConn.getPlantsToWaterInAquaGarden()
            nPlants = len(plants['fieldID'])
            for i in range(0, nPlants):
                sFields = self._getAllFieldIDsFromFieldIDAndSizeAsString(plants['fieldID'][i], plants['sx'][i], plants['sy'][i])
                self._httpConn.waterPlantInAquaGarden(plants['fieldID'][i], sFields)
        except:
            self._logGarden.error('Wassergarten konnte nicht bewässert werden.')
        else:
            self._logGarden.info(f'Im Wassergarten wurden {nPlants} Pflanzen gegossen.')
            print(f'Im Wassergarten wurden {nPlants} Pflanzen gegossen.')

    def harvest(self):
        """
        Erntet alles im Wassergarten.
        """
        try:
            self._httpConn.harvestAquaGarden()
        except:
            raise
        else:
            pass

    def growPlant(self, plantID, sx, sy, edge, amount):
        """Grows a watergarden plant of any size and type."""
        planted = 0
        emptyFields = self.getEmptyAquaFields()
        try:
            for field in range(1, self._MAX_FIELDS + 1):
                if planted == amount: break

                fieldsToPlant = self._getAllFieldIDsFromFieldIDAndSizeAsIntList(field, sx, sy)

                if (self._isPlantGrowableOnField(field, emptyFields, fieldsToPlant, edge)):
                    self._httpConn.growAquaPlant(field, plantID)
                    planted += 1

                    # Nach dem Anbau belegte Felder aus der Liste der leeren Felder loeschen
                    fieldsToPlantSet = set(fieldsToPlant)
                    emptyFieldsSet = set(emptyFields)
                    tmpSet = emptyFieldsSet - fieldsToPlantSet
                    emptyFields = list(tmpSet)

        except:
            self._logGarden.error(f'Im Wassergarten konnte nicht gepflanzt werden.')
            return 0
        else:
            msg = f'Im Wassergarten wurden {planted} Pflanzen gepflanzt.'
            if emptyFields:
                msg = msg + f' Im Wassergarten sind noch {len(emptyFields)} leere Felder vorhanden.'
            self._logGarden.info(msg)
            print(msg)
            return planted

    def removeWeed(self):
        """
        Entfernt alles Unkraut, Steine und Maulwürfe, wenn ausreichend Geld vorhanden ist.
        """
        weedFieldsAqua = self.getWeedFields()
        freeFields = []
        for fieldID in weedFieldsAqua:
            try:
                result = self._httpConn.removeWeedOnFieldInAquaGarden(self._id, fieldID)
            except:
                self._logGarden.error(
                    f'Feld {fieldID} im Auqagarten {self._id} konnte nicht von Unkraut befreit werden!')
            else:
                if result == 1:
                    self._logGarden.info(f'Feld {fieldID} im Auqagarten {self._id} wurde von Unkraut befreit!')
                    freeFields.append(fieldID)
                else:
                    self._logGarden.error(
                        f'Feld {fieldID} im Auqagarten {self._id} konnte nicht von Unkraut befreit werden!')

        self._logGarden.info(f'Im Auqagarten {self._id} wurden {len(freeFields)} Felder von Unkraut befreit.')


class HerbGarden(Garden):
    def __init__(self, httpConnection):
        Garden.__init__(self, httpConnection, 201)
        self.__setValidFields()
        self.__jContent = self._httpConn.initHerbGarden()
        self.__exchange = self.__jContent['exchange']
        self.__setHerbGardenInfo(self.__jContent)

    def __setValidFields(self):
        self._VALID_FIELDS = {}
        for x in range(1, 205, 34):
            for y in range(x, x+7, 2):
                self._VALID_FIELDS.update({y: self._getAllFieldIDsFromFieldIDAndSizeAsString(y, 2, 2)})

    def __setHerbGardenInfo(self, jContent):
        self.__jContent = jContent
        self.__info = self.__jContent['info']
        self.__weed = self.__jContent['weed']

    def _isPlantGrowableOnField(self, fieldID, emptyFields):
        """Prüft anhand mehrerer Kriterien, ob ein Anpflanzen möglich ist."""
        # Betrachtetes Feld darf nicht besetzt sein
        if not (fieldID in emptyFields): return False
        return True

    def harvest(self): # TODO: proof if any harvestable
        jContent = self._httpConn.harvestHerbGarden()
        if jContent['status'] == 'error':
            msg = jContent['message']
        elif jContent['status'] == 'ok':
            msg = jContent['harvestMsg']
            self.__setHerbGardenInfo(jContent)
        print(msg)
        self._logGarden.info(msg)

    def removeWeed(self): #Abfrage if jContent['weed']
        # msg = "In deinem Kräutergarten ist kein Unkraut."
        # if self.__weed:
        jContent = self._httpConn.removeWeedInHerbGarden()
        msg = jContent.get('message', None)
        self.__setHerbGardenInfo(jContent)
        self._logGarden.info(msg)

    def getEmptyFields(self):
        """Sucht im JSON Content nach Felder die leer sind und gibt diese zurück."""
        emptyFields = []
        for field in self.__jContent['garden']:
            if self.__jContent['garden'][field][0] == 0 and int(field) in self._VALID_FIELDS.keys():
                emptyFields.append(int(field))

        #Sortierung über ein leeres Array ändert Objekttyp zu None
        if len(emptyFields) > 0:
            emptyFields.sort(reverse=False)

        return emptyFields

    def growPlant(self, bot: WurzelBot, amount=24):
        """Grows a plant of any size."""
        herbID = self.__info.get('herbid')
        herb_stock = bot.storage.getStockByProductID(herbID)

        while not herb_stock >= amount:
            self.exchangeHerb(bot)
            herb_stock = bot.storage.getStockByProductID(herbID)
        
        planted = 0
        emptyFields = self.getEmptyFields()

        try:
            for field in self._VALID_FIELDS.keys():
                if planted == amount: 
                    break

                if (self._isPlantGrowableOnField(int(field), emptyFields)):
                    fields = self._getAllFieldIDsFromFieldIDAndSizeAsString(field, 2, 2)
                    self._httpConn.growPlant(field, herbID, self._id, fields)
                    planted += 1

                    #Nach dem Anbau belegte Felder aus der Liste der leeren Felder loeschen
                    fieldsToPlantSet = {field}
                    emptyFieldsSet = set(emptyFields)
                    tmpSet = emptyFieldsSet - fieldsToPlantSet
                    emptyFields = list(tmpSet)
        except:
            self._logGarden.error(f'Im Garten {self._id} konnte nicht gepflanzt werden.')
            return 0
        else:
            msg = f'Im Garten {self._id} wurden {planted} Pflanzen gepflanzt.'
            if emptyFields: 
                msg = msg + f' Im Garten {self._id} sind noch leere Felder vorhanden.'
            self._logGarden.info(msg)
            print(msg)
            return planted
        

    def exchangeHerb(self, bot: WurzelBot):
        exchange = {}
        buy_price = {}

        for plant in self.__exchange:
            pid = plant['plant']
            amount = plant['amount']
            exchange.update({pid: amount})
            total = amount * bot.productData.getProductByID(pid).getPriceNPC()
            buy_price.update({pid: total})

        sorted_dict = sorted(buy_price.items(), key=lambda x:x[1])
        cheapest_plant = next(iter(sorted_dict))[0]

        stock = bot.storage.getStockByProductID(cheapest_plant)
        amount = exchange[cheapest_plant]

        if not stock >= amount:
            bot.doBuyFromShop(bot.productData.getProductByID(cheapest_plant).getName(), amount)
        self._httpConn.exchangeHerb(cheapest_plant)

        bot.storage.updateNumberInStock()