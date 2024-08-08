#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import Counter, namedtuple
import logging, i18n
from src.core.User import User
from src.core.HTTPCommunication import HTTPConnection
from src.product.ProductData import ProductData

i18n.load_path.append('lang')

class Garden():
    _LEN_X = 17
    _LEN_Y = 12
    _MAX_FIELDS = _LEN_X * _LEN_Y
    _PLANT_PER_REQUEST = 6

    def __init__(self, httpConnection: HTTPConnection, gardenID):
        self._httpConn = httpConnection
        self._user = User()
        self._id = gardenID
        self._logGarden = logging.getLogger('bot.Garden_' + str(gardenID))
        self._logGarden.setLevel(logging.DEBUG)

    def _getAllFieldIDsFromFieldIDAndSizeAsString(self, fieldID, sx, sy):
        """
        Rechnet anhand der fieldID und Größe der Pflanze (sx, sy) alle IDs aus und gibt diese als String zurück.
        """
        #BG- Изчислява всички ID-та въз основа на ID-то на полето и размера на растението (sx, sy) и ги връща като низ.

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
        #BG- Индекси на полетата (x), които се връщат за растения с размери 1, 2 и 4 полета.
        #BG- Важно при поливане: всички индекси трябва да бъдат посочени там.
        #BG- (Както тези, маркирани с x, така и тези, маркирани с o).
        #BG- x: Идентификатор на полето
        #BG- o: Добавени полета въз основа на размера
        #BG- +---+   +---+---+   +---+---+
        #BG- | x |   | x | o |   | x | o |
        #BG- +---+   +---+---+   +---+---+
        #BG-                     | o | o |
        #BG-                     +---+---+

        if (sx == 1 and sy == 1): return str(fieldID)
        if (sx == 2 and sy == 1): return str(fieldID) + ',' + str(fieldID + 1)
        if (sx == 1 and sy == 2): return str(fieldID) + ',' + str(fieldID + 17)
        if (sx == 2 and sy == 2): return str(fieldID) + ',' + str(fieldID + 1) + ',' + str(fieldID + 17) + ',' + str(fieldID + 18)
        self._logGarden.debug(f'Error der plantSize --> sx: {sx} sy: {sy}')

    def _getAllFieldIDsFromFieldIDAndSizeAsIntList(self, fieldID, sx, sy):
        """
        Calculates all IDs based on the fieldID and size of the plant (sx, sy) and returns them as an integer list.
        """
        #BG- Изчислява всички ID-та въз основа на ID-то на полето и размера на растението (sx, sy) и ги връща като списък с цели числа.
        sFields = self._getAllFieldIDsFromFieldIDAndSizeAsString(fieldID, sx, sy)
        listFields = sFields.split(',') #Stringarray #BG- Масив от низове

        for i in range(0, len(listFields)):
            listFields[i] = int(listFields[i])

        return listFields

    def _isPlantGrowableOnField(self, fieldID, emptyFields, fieldsToPlant, sx):
        """Prüft anhand mehrerer Kriterien, ob ein Anpflanzen möglich ist."""
        # Betrachtetes Feld darf nicht besetzt sein
        #BG- Разглежданото поле не трябва да е заето.

        if not (fieldID in emptyFields): return False

        # Anpflanzen darf nicht außerhalb des Gartens erfolgen
        # Dabei reicht die Betrachtung in x-Richtung, da hier ein
        # "Zeilenumbruch" stattfindet. Die y-Richtung ist durch die
        # Abfrage abgedeckt, ob alle benötigten Felder frei sind.
        # Felder außerhalb (in y-Richtung) des Gartens sind nicht leer,
        # da sie nicht existieren.

        #BG- Засаждане не е разрешено извън градината.
        #BG- В този случай е достатъчно да се разгледа само x-оста, тъй като тук се извършва "прекъсване на реда".
        #BG- „Прекъсване на реда“ се извършва. Y-оста е обхваната от проверката дали всички необходими полета са свободни.
        #BG- Проверка дали всички необходими полета са свободни.
        #BG- Полетата извън градината (по y-оста) не са празни, защото не съществуват,
        #BG- тъй като те не съществуват.

        if not ((self._MAX_FIELDS - fieldID)%self._LEN_X >= sx - 1): return False
        fieldsToPlantSet = set(fieldsToPlant)
        emptyFieldsSet = set(emptyFields)

        # Alle benötigten Felder der Pflanze müssen leer sein
        #BG- Всички необходими полета на растението трябва да бъдат празни.
        if not (fieldsToPlantSet.issubset(emptyFieldsSet)): return False
        return True

    def getID(self):
        """Returns the ID of garden."""
        #BG- Връща идентификационния номер на градината.
        return self._id

    def water(self):
        """Water all plants in the garden"""
        #BG- Градината с gardenID се полива напълно.
        self._logGarden.info(f'Gieße alle Pflanzen im Garten {self._id}.')
        #BG- self._logGarden.info(f'Полей всички растения в градината. {self._id}.')
        try:
            plants = self._httpConn.getPlantsToWaterInGarden(self._id)
            nPlants = len(plants['fieldID'])
            if nPlants and self._user.has_watering_gnome_helper():
                self._httpConn.water_all_plants_in_garden()
            else:
                for i in range(0, nPlants):
                    sFields = self._getAllFieldIDsFromFieldIDAndSizeAsString(plants['fieldID'][i], plants['sx'][i], plants['sy'][i])
                    self._httpConn.waterPlantInGarden(self._id, plants['fieldID'][i], sFields)
        except:
            self._logGarden.error(f'Garten {self._id} konnte nicht bewässert werden.')
            #BG- self._logGarden.error(f'Градина {self._id} не може да бъде поливана.')
        else:
            self._logGarden.info(f'Im Garten {self._id} wurden {nPlants} Pflanzen gegossen.')
            #BG-self._logGarden.info(f'В градината {self._id} са поляти {nPlants} растения.')

            print(f'Im Garten {self._id} wurden {nPlants} Pflanzen gegossen.')
            #BG- print(f'В градината {self._id} са поляти {nPlants} растения.')

    def getEmptyFields(self):
        """Returns all empty fields in the garden."""
        #BG- """Връща всички празни полета в градината."""
        try:
            return self._httpConn.getEmptyFieldsOfGarden(self._id)
        except:
            self._logGarden.error(f'Konnte leere Felder von Garten {self._id} nicht ermitteln.')
            #BG- self._logGarden.error(f'Неуспешно определение на празни полета в градина {self._id}.')

    def get_grown_fields(self):
        """Returns all grown fields in the garden."""
        try:
            return self._httpConn.getEmptyFieldsOfGarden(self._id, param="grown")
        except:
            self._logGarden.error(f'Konnte bepflanzte Felder von Garten {self._id} nicht ermitteln.')
            #BG- self._logGarden.error(f'Неуспешно определение на празни полета в градина {self._id}.')

    def getWeedFields(self):
        """Returns all weed fields in the garden."""
        #BG- """Връща всички полета с плевели в градината."""
        try:
            return self._httpConn.getWeedFieldsOfGarden(self._id)
        except:
            self._logGarden.error(f'Konnte Unkraut-Felder von Garten {self._id} nicht ermitteln.')
            #BG- self._logGarden.error(f'Неуспешно определение на полета с плевели в градина {self._id}.')

    def getGrowingPlants(self):
        """Returns all growing plants in the garden."""
        #BG- """Връща всички растящи растения в градината."""

        try:
            return Counter(self._httpConn.getGrowingPlantsOfGarden(self._id))
        except:
            self._logGarden.error('Could not determine growing plants of garden ' + str(self._id) + '.')
            #BG- self._logGarden.error('Неуспешно определение на растящите растения в градина ' + str(self._id) + '.')

    def getNextWaterHarvest(self):
        """Returns all growing plants in the garden."""
        #BG- """Връща всички растящи растения в градината."""

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
            #BG- self._logGarden.error('Неуспешно определение на растящите растения в градина ' + str(self._id) + '.')


    def harvest(self):
        """Harvest everything"""
        #BG- """Събери всичко."""

        try:
            self._httpConn.harvestGarden(self._id)
        except:
            raise

    def harvest_unfinished(self):
        #BG- """Отглежда растение от всякакъв размер."""

        grown_fields = self.get_grown_fields()
        print('grown_fields:', grown_fields)

        try:
            for field, plant_id in grown_fields.items():
                sx = ProductData().get_product_by_id(plant_id).get_sx()
                sy = ProductData().get_product_by_id(plant_id).get_sy()
                fields = self._getAllFieldIDsFromFieldIDAndSizeAsString(field, sx, sy)
                self._httpConn.harvest_unfinished(plant_id, field, fields)
        except:
            raise

    def grow(self, plantID, sx, sy, amount):
        """Grows a plant of any size."""
        #BG- """Отглежда растение от всякакъв размер."""

        planted = 0
        emptyFields = self.getEmptyFields()

        try:
            to_plant = {}
            for field in range(1, self._MAX_FIELDS+1):
                
                if planted == amount: break
                fieldsToPlant = self._getAllFieldIDsFromFieldIDAndSizeAsIntList(field, sx, sy)

                if (self._isPlantGrowableOnField(field, emptyFields, fieldsToPlant, sx)):
                    fields = self._getAllFieldIDsFromFieldIDAndSizeAsString(field, sx, sy) # get fields for one plant
                    to_plant.update({field: fields}) #collect all plants for a request

                    #Nach dem Anbau belegte Felder aus der Liste der leeren Felder loeschen
                    #BG- След отглеждането, изтрийте заетите полета от списъка на празните полета
                    fieldsToPlantSet = set(fieldsToPlant)
                    emptyFieldsSet = set(emptyFields)
                    tmpSet = emptyFieldsSet - fieldsToPlantSet
                    emptyFields = list(tmpSet)
                
                if len(to_plant) == self._PLANT_PER_REQUEST or (field == self._MAX_FIELDS and len(to_plant) > 0):
                    self._httpConn.grow(to_plant, plantID, self._id)
                    planted += len(to_plant)
                    to_plant = {}

        except:
            self._logGarden.error(f'Im Garten {self._id} konnte nicht gepflanzt werden.')
            #BG- self._logGarden.error(f'В градината {self._id} не може да се засади.')

            return 0
        else:
            msg = f'Im Garten {self._id} wurden {planted} Pflanzen gepflanzt.'
            #BG- msg = f'В градината {self._id} са засадени {planted} растения.'

            if emptyFields:
                msg = msg + f' Im Garten {self._id} sind noch leere Felder vorhanden.'
                #BG- msg = msg + f' В градината {self._id} все още има празни полета.'

            self._logGarden.info(msg)
            print(msg)
            return planted

    def remove_weeds(self):
        """
        Entfernt alles Unkraut, Steine und Maulwürfe, wenn ausreichend Geld vorhanden ist.
        """
        #BG- Премахва всички плевели, камъни и кърлежи, ако има достатъчно пари.

        weedFields = self.getWeedFields()
        freeFields = []
        for fieldID in weedFields:
            try:
                result = self._httpConn.removeWeedOnFieldInGarden(self._id, fieldID)
            except:
                self._logGarden.error(f'Feld {fieldID} im Garten {self._id} konnte nicht von Unkraut befreit werden!')
                #BG- self._logGarden.error(f'Полето {fieldID} в градината {self._id} не може да бъде освободено от плевели!')

            else:
                if result == 1:
                    self._logGarden.info(f'Feld {fieldID} im Garten {self._id} wurde von Unkraut befreit!')
                    #BG- self._logGarden.info(f'Полето {fieldID} в градината {self._id} беше освободено от плевели!')

                    freeFields.append(fieldID)
                else:
                    self._logGarden.error(f'Feld {fieldID} im Garten {self._id} konnte nicht von Unkraut befreit werden!')
                    #BG- self._logGarden.error(f'Полето {fieldID} в градината {self._id} не може да бъде освободено от плевели!')


        self._logGarden.info(f'Im Garten {self._id} wurden {len(freeFields)} Felder von Unkraut befreit.')
        #BG- self._logGarden.info(f'В градината {self._id} бяха освободени от плевели {len(freeFields)} полета.')



class AquaGarden(Garden):
    def __init__(self, httpConnection):
        Garden.__init__(self, httpConnection, 101)
        self.__setInnerFields()
        self.__setOuterFields()
        self._PLANT_PER_REQUEST = 11

    def __setInnerFields(self, distance=2):
        """defines the fieldID's of the inner watergarden planting area"""
        #BG- """Задава fieldID-тата на полетата във вътрешната област за засаждане във водната градина."""

        self._INNER_FIELDS = []
        for i in range(distance, self._LEN_Y-distance):
            self._INNER_FIELDS.extend(range(i * self._LEN_X + distance + 1, (i + 1) * self._LEN_X - distance + 1))

    def __setOuterFields(self):
        """defines the fieldID's of the outer watergarden planting area"""
        #BG- """Задава fieldID-тата на полетата във външната област за засаждане във водната градина."""

        temp_fields = list(range(1, self._MAX_FIELDS+1))
        self._OUTER_FIELDS = [x for x in temp_fields if x not in self._INNER_FIELDS]

    def _isPlantGrowableOnField(self, fieldID, emptyFields, fieldsToPlant, edge):
        """Prüft anhand mehrerer Kriterien, ob ein Anpflanzen möglich ist."""
        #BG- """Проверява чрез няколко критерия дали е възможно засаждане."""

        # Betrachtetes Feld darf nicht besetzt sein
        #BG- Полето, което се разглежда, не трябва да е заето

        if not (fieldID in emptyFields): return False

        #Randpflanze im Wassergarten
        #BG- # Растение на ръба във водната градина

        if edge == 1:
            if not [x for x in fieldsToPlant if x in self._OUTER_FIELDS] == fieldsToPlant: return False

        #Wasserpflanzen im Wassergarten
        #BG- Водни растения във водната градина

        if edge == 0:
            if not [x for x in fieldsToPlant if x in self._INNER_FIELDS] == fieldsToPlant: return False

        fieldsToPlantSet = set(fieldsToPlant)
        emptyFieldsSet = set(emptyFields)

        # Alle benötigten Felder der Pflanze müssen leer sein
        #BG- # Всички необходими полета за растението трябва да бъдат празни

        if not (fieldsToPlantSet.issubset(emptyFieldsSet)): return False
        return True

    def getEmptyAquaFields(self):
        """
        Gibt alle leeren Felder des Gartens zurück.
        """
        #BG- Връща всички празни полета на градината.

        try:
            tmpEmptyAquaFields = self._httpConn.getEmptyFieldsAqua()
        except:
            self._logGarden.error('Konnte leere Felder von AquaGarten nicht ermitteln.')
            #BG- self._logGarden.error('Неуспешно определение на празни полета в Аква-градината.')

        else:
            return tmpEmptyAquaFields

    def water(self):
        try:
            plants = self._httpConn.getPlantsToWaterInAquaGarden()
            nPlants = len(plants['fieldID'])
            if nPlants and self._user.has_watering_gnome_helper():
                self._httpConn.water_all_plants_in_aquagarden()
            else:
                for i in range(0, nPlants):
                    sFields = self._getAllFieldIDsFromFieldIDAndSizeAsString(plants['fieldID'][i], plants['sx'][i], plants['sy'][i])
                    self._httpConn.waterPlantInAquaGarden(plants['fieldID'][i], sFields)
        except:
            self._logGarden.error('Wassergarten konnte nicht bewässert werden.')
            #BG- self._logGarden.error('Водната градина не може да бъде поливан.')

        else:
            self._logGarden.info(f'Im Wassergarten wurden {nPlants} Pflanzen gegossen.')
            #BG- self._logGarden.info(f'Във водната градина бяха поляти {nPlants} растения.')

            print(f'Im Wassergarten wurden {nPlants} Pflanzen gegossen.')
            #BG- print(f'Във водната градина бяха поляти {nPlants} растения.')


    def harvest(self):
        """
        Erntet alles im Wassergarten.
        """
        #BG- Събира всичко във водната градина.

        try:
            self._httpConn.harvestAquaGarden()
        except:
            raise
        else:
            pass

    def grow(self, plantID, sx, sy, edge, amount):
        """Grows a watergarden plant of any size and type."""
        #BG- """Отглежда водно растение във водната градина с всякакъв размер и вид."""

        planted = 0
        emptyFields = self.getEmptyAquaFields()
        to_plant = {}
        try:
            for field in range(1, self._MAX_FIELDS + 1):
                if planted == amount: break

                fieldsToPlant = self._getAllFieldIDsFromFieldIDAndSizeAsIntList(field, sx, sy)

                if (self._isPlantGrowableOnField(field, emptyFields, fieldsToPlant, edge)):
                    to_plant.update({field: None}) #collect all plants for a request

                    # Nach dem Anbau belegte Felder aus der Liste der leeren Felder loeschen
                    #BG- След отглеждането, изтрийте заетите полета от списъка на празните полета
                    fieldsToPlantSet = set(fieldsToPlant)
                    emptyFieldsSet = set(emptyFields)
                    tmpSet = emptyFieldsSet - fieldsToPlantSet
                    emptyFields = list(tmpSet)

                if (len(to_plant) == self._PLANT_PER_REQUEST) or (field == self._MAX_FIELDS and len(to_plant) > 0):
                    self._httpConn.growAquaPlant(to_plant, plantID)
                    planted += len(to_plant)
                    to_plant = {}
                    
        except:
            self._logGarden.error(f'Im Wassergarten konnte nicht gepflanzt werden.')
            #BG- self._logGarden.error(f'Във водната градина не може да се засади.')

            return 0
        else:
            msg = f'Im Wassergarten wurden {planted} Pflanzen gepflanzt.'
            #BG- msg = f'Във водната градина са засадени {planted} растения.'

            if emptyFields:
                msg = msg + f' Im Wassergarten sind noch {len(emptyFields)} leere Felder vorhanden.'
                #BG- msg = msg + f' Във водната градина все още има {len(emptyFields)} празни полета.'

            self._logGarden.info(msg)
            print(msg)
            return planted

    def remove_weeds(self):
        """
        Entfernt alles Unkraut, Steine und Maulwürfe, wenn ausreichend Geld vorhanden ist.
        """
        #BG- Премахва всички плевели, камъни и кърлежи, ако има достатъчно пари.

        weedFieldsAqua = self.getWeedFields()
        freeFields = []
        for fieldID in weedFieldsAqua:
            try:
                result = self._httpConn.removeWeedOnFieldInGarden(self._id, fieldID)
            except:
                self._logGarden.error(
                    f'Feld {fieldID} im Auqagarten {self._id} konnte nicht von Unkraut befreit werden!')
                    #BG- f'Полето {fieldID} в Аква-градината {self._id} не може да бъде освободено от плевели!')

            else:
                if result == 1:
                    self._logGarden.info(f'Feld {fieldID} im Auqagarten {self._id} wurde von Unkraut befreit!')
                    #BG- self._logGarden.info(f'Полето {fieldID} в Аква-градината {self._id} беше освободено от плевели!')

                    freeFields.append(fieldID)
                else:
                    self._logGarden.error(
                        f'Feld {fieldID} im Auqagarten {self._id} konnte nicht von Unkraut befreit werden!')
                        #BG- f'Полето {fieldID} в Аква-градината {self._id} не може да бъде освободено от плевели!')


        self._logGarden.info(f'Im Auqagarten {self._id} wurden {len(freeFields)} Felder von Unkraut befreit.')
        #BG- self._logGarden.info(f'В Аква-градината {self._id} бяха освободени от плевели {len(freeFields)} полета.')


class HerbGarden(Garden):
    def __init__(self, httpConnection):
        Garden.__init__(self, httpConnection, 201)
        self.__setValidFields()
        self.__jContent = self._httpConn.init_herb_garden()
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
        jContent = self._httpConn.harvest_herb_garden()
        if jContent['status'] == 'error':
            msg = jContent['message']
        elif jContent['status'] == 'ok':
            msg = jContent['harvestMsg']
            self.__setHerbGardenInfo(jContent)
        print(msg)
        self._logGarden.info(msg)

    def remove_weeds(self): #Abfrage if jContent['weed']
        # msg = "In deinem Kräutergarten ist kein Unkraut."
        # if self.__weed:
        jContent = self._httpConn.remove_weed_in_herb_garden()
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

    def grow_plant(self, bot, amount=24):
        """Grows a plant of any size."""
        herbID = self.__info.get('herbid')
        herb_stock = bot.stock.get_stock_by_product_id(herbID)

        if not self.__info.get('canPlant'):
            return
        
        if self.__info.get('send') >= self.__info.get('amount'):
            return

        while not herb_stock >= amount:
            self.exchangeHerb(bot)
            herb_stock = bot.stock.get_stock_by_product_id(herbID)
        
        planted = 0
        emptyFields = self.getEmptyFields()
        to_plant = {}

        try:
            for field in self._VALID_FIELDS.keys():
                if planted == amount: 
                    break

                if (self._isPlantGrowableOnField(int(field), emptyFields)):
                    fields = self._getAllFieldIDsFromFieldIDAndSizeAsString(field, 2, 2)
                    to_plant.update({field: fields}) #collect all plants for a request

                    #Nach dem Anbau belegte Felder aus der Liste der leeren Felder loeschen
                    fieldsToPlantSet = {field}
                    emptyFieldsSet = set(emptyFields)
                    tmpSet = emptyFieldsSet - fieldsToPlantSet
                    emptyFields = list(tmpSet)

                if len(to_plant) == self._PLANT_PER_REQUEST or (field == self._MAX_FIELDS and len(to_plant) > 0):
                    self._httpConn.growPlant(to_plant, herbID, self._id)
                    planted += len(to_plant)
                    to_plant = {}
                    
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
        

    def exchangeHerb(self, bot):
        productData = ProductData()
        exchange = {}
        buy_price = {}

        for plant in self.__exchange:
            pid = plant['plant']
            amount = plant['amount']
            exchange.update({pid: amount})
            total = amount * productData.get_product_by_id(pid).get_price_npc()
            buy_price.update({pid: total})

        sorted_dict = sorted(buy_price.items(), key=lambda x:x[1])
        cheapest_plant = next(iter(sorted_dict))[0]

        stock = bot.stock.get_stock_by_product_id(cheapest_plant)
        amount = exchange[cheapest_plant]

        if not stock >= amount:
            bot.buy_from_shop(productData.get_product_by_id(cheapest_plant).get_name(), amount)
        self._httpConn.exchange_herb(cheapest_plant)

        bot.stock.update()