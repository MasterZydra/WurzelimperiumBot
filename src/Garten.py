#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import Counter, namedtuple
import logging, i18n
from src.core.HTTPCommunication import HTTPConnection

i18n.load_path.append('lang')

class Garden():
    _LEN_X = 17
    _LEN_Y = 12
    _MAX_FIELDS = _LEN_X * _LEN_Y

    def __init__(self, httpConnection: HTTPConnection, gardenID):
        self._httpConn = httpConnection
        self._id = gardenID
        self._logGarden = logging.getLogger(f'bot.Garden_{gardenID}')
        self._logGarden.setLevel(logging.DEBUG)

    def _getAllFieldIDsFromFieldIDAndSizeAsString(self, fieldID, sx, sy):
        """
        Calculates all field IDs based on the fieldID and size of the plant (sx, sy) and returns them as a string.
        xRuffKez: Let's use elif instead of if, to make reading tiles faster ;)
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

        if sx == 1 and sy == 1:
            return str(fieldID)
        elif sx == 2 and sy == 1:
            return f"{fieldID},{fieldID + 1}"
        elif sx == 1 and sy == 2:
            return f"{fieldID},{fieldID + 17}"
        elif sx == 2 and sy == 2:
            return f"{fieldID},{fieldID + 1},{fieldID + 17},{fieldID + 18}"
        else:
            self._logGarden.debug(f'Error in plantSize --> sx: {sx} sy: {sy}')

    def _getAllFieldIDsFromFieldIDAndSizeAsIntList(self, fieldID, sx, sy):
        """
        Calculates all IDs based on the fieldID and size of the plant (sx, sy) and returns them as an integer list.
        """
        sFields = self._getAllFieldIDsFromFieldIDAndSizeAsString(fieldID, sx, sy)
        return [int(field) for field in sFields.split(',')]

    def _isPlantGrowableOnField(self, fieldID, emptyFields, fieldsToPlant, sx):
        """Checks if planting is possible based on multiple criteria."""
        # The considered field must not be occupied
        if fieldID not in emptyFields:
            return False

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

        if (self._MAX_FIELDS - fieldID) % self._LEN_X < sx - 1:
            return False

        # All required fields of the plant must be empty
        if not set(fieldsToPlant).issubset(set(emptyFields)):
            return False

        return True

    def getID(self):
        """Returns the ID of garden."""
        #BG- Връща идентификационния номер на градината.
        return self._id

    def getEmptyFields(self):
        """Returns all empty fields in the garden."""
        try:
            return self._httpConn.getEmptyFieldsOfGarden(self._id)
        except:
            self._logGarden.error(f'Failed to determine empty fields in garden {self._id}.')

    def waterPlants(self):
        """Water all plants in the garden."""
        self._logGarden.info(f'Watering all plants in garden {self._id}.')
        try:
            plants = self._httpConn.getPlantsToWaterInGarden(self._id)
            for i, fieldID in enumerate(plants['fieldID']):
                sFields = self._getAllFieldIDsFromFieldIDAndSizeAsString(fieldID, plants['sx'][i], plants['sy'][i])
                self._httpConn.waterPlantInGarden(self._id, fieldID, sFields)
            nPlants = len(plants['fieldID'])
            self._logGarden.info(f'{nPlants} plants watered in garden {self._id}.')
            print(f'{nPlants} plants watered in garden {self._id}.')
        except Exception as e:
            self._logGarden.error(f'Failed to water plants in garden {self._id}. Error: {e}')


    def getWeedFields(self):
        """Returns all weed fields in the garden."""
        try:
            return self._httpConn.getWeedFieldsOfGarden(self._id)
        except:
            self._logGarden.error(f'Failed to determine weed fields in garden {self._id}.')

    def getGrowingPlants(self):
        """Returns all growing plants in the garden."""
        try:
            return Counter(self._httpConn.getGrowingPlantsOfGarden(self._id))
        except:
            self._logGarden.error(f'Failed to determine growing plants of garden {self._id}.')

    def getNextWaterHarvest(self):
        """Returns the next water or harvest time in the garden."""
        try:
            overall_time = []
            max_water_time = 86400  # Maximum time between watering and harvest
            garden = self._httpConn._changeGarden(self._id).get('garden')
            for field in garden.values():
                if field[0] in [41, 42, 43, 45]:  # Skip fields with special plants
                    continue
                water_time = field[4]  # Time of last watering
                harvest_time = field[3]  # Time of next harvest
                if harvest_time - water_time > max_water_time:
                    overall_time.append(water_time + max_water_time)
                overall_time.append(harvest_time)
            return min(overall_time) if overall_time else None
        except:
            self._logGarden.error(f'Failed to determine the next water/harvest time in garden {self._id}.')

    def harvest(self):
        """Harvest all crops in the garden."""
        try:
            self._httpConn.harvestGarden(self._id)
        except Exception as e:
            raise e


    def growPlant(self, plantID, sx, sy, amount):
        """Grow the specified amount of plants with the given ID and size in the garden."""
        #BG- """Отглежда определено количество растения с даден идентификатор и размер в градината."""

        planted = 0
        emptyFields = self.getEmptyFields()

        try:
            for field in range(1, self._MAX_FIELDS + 1):
                if planted == amount:
                    break

                fieldsToPlant = self._getAllFieldIDsFromFieldIDAndSizeAsIntList(field, sx, sy)

                if self._isPlantGrowableOnField(field, emptyFields, fieldsToPlant, sx):
                    fields = self._getAllFieldIDsFromFieldIDAndSizeAsString(field, sx, sy)
                    self._httpConn.growPlant(field, plantID, self._id, fields)
                    planted += 1

                    # Remove planted fields from the list of empty fields
                    #BG- Премахнете засадените полета от списъка с празни полета
                    fieldsToPlantSet = set(fieldsToPlant)
                    emptyFieldsSet = set(emptyFields)
                    emptyFields = list(emptyFieldsSet - fieldsToPlantSet)

        except Exception as e:
            self._logGarden.error(f'Failed to grow plants in garden {self._id}.')
            #BG- self._logGarden.error(f'Неуспешно отглеждане на растения в градина {self._id}.')
            return 0

        else:
            msg = f'{planted} plants were grown in garden {self._id}.'
            #BG- msg = f'{planted} растения са отгледани в градина {self._id}.'

            if emptyFields:
                msg += f' There are still empty fields in garden {self._id}.'
                #BG- msg += f' В градина {self._id} все още има празни полета.'

            self._logGarden.info(msg)
            print(msg)
            return planted


    def removeWeed(self):
        """
        Removes all weeds, stones, and moles if enough money is available.
        """
        #BG- Премахва всички плевели, камъни и кърлежи, ако има достатъчно пари.

        weedFields = self.getWeedFields()
        freeFields = []

        for fieldID in weedFields:
            try:
                result = self._httpConn.removeWeedOnFieldInGarden(self._id, fieldID)
            except Exception as e:
                self._logGarden.error(f'Field {fieldID} in garden {self._id} could not be cleared of weeds!')
                #BG- self._logGarden.error(f'Полето {fieldID} в градината {self._id} не може да бъде освободено от плевели!')
            else:
                if result == 1:
                    self._logGarden.info(f'Field {fieldID} in garden {self._id} was cleared of weeds!')
                    #BG- self._logGarden.info(f'Полето {fieldID} в градината {self._id} беше освободено от плевели!')
                    freeFields.append(fieldID)
                else:
                    self._logGarden.error(f'Field {fieldID} in garden {self._id} could not be cleared of weeds!')
                    #BG- self._logGarden.error(f'Полето {fieldID} в градината {self._id} не може да бъде освободено от плевели!')

        self._logGarden.info(f'{len(freeFields)} fields were cleared of weeds in garden {self._id}.')
        #BG- self._logGarden.info(f'В градината {self._id} бяха освободени от плевели {len(freeFields)} полета.')

class AquaGarden(Garden):
    def __init__(self, httpConnection):
        Garden.__init__(self, httpConnection, 101)
        self.__setInnerFields()
        self.__setOuterFields()

    def __setInnerFields(self, distance=2):
        """Defines the fieldIDs of the inner water garden planting area."""
        self._INNER_FIELDS = []
        for i in range(distance, self._LEN_Y-distance):
            self._INNER_FIELDS.extend(range(i * self._LEN_X + distance + 1, (i + 1) * self._LEN_X - distance + 1))

    def __setOuterFields(self):
        """Defines the fieldIDs of the outer water garden planting area."""
        temp_fields = list(range(1, self._MAX_FIELDS+1))
        self._OUTER_FIELDS = [x for x in temp_fields if x not in self._INNER_FIELDS]

    def _isPlantGrowableOnField(self, fieldID, emptyFields, fieldsToPlant, edge):
        """Checks multiple criteria to determine if planting is possible."""
        # Betrachtetes Feld darf nicht besetzt sein
        if fieldID not in emptyFields:
            return False

        # Randpflanze im Wassergarten
        if edge == 1:
            if not [x for x in fieldsToPlant if x in self._OUTER_FIELDS] == fieldsToPlant:
                return False

        # Wasserpflanzen im Wassergarten
        if edge == 0:
            if not [x for x in fieldsToPlant if x in self._INNER_FIELDS] == fieldsToPlant:
                return False

        fieldsToPlantSet = set(fieldsToPlant)
        emptyFieldsSet = set(emptyFields)

        # Alle benötigten Felder der Pflanze müssen leer sein
        if not fieldsToPlantSet.issubset(emptyFieldsSet):
            return False
        return True

    def getEmptyAquaFields(self):
        """Returns all empty fields of the garden."""
        # Gibt alle leeren Felder des Gartens zurück.

        try:
            return self._httpConn.getEmptyFieldsAqua()
        except:
            self._logGarden.error('Could not determine empty fields of AquaGarden.')


    def waterPlants(self):
        """Waters all plants in the aqua garden."""
        self._logGarden.info(f'Watering all plants in the aqua garden {self._id}.')
        try:
            plants = self._httpConn.getPlantsToWaterInAquaGarden()
            for i, fieldID in enumerate(plants['fieldID']):
                sFields = self._getAllFieldIDsFromFieldIDAndSizeAsString(fieldID, plants['sx'][i], plants['sy'][i])
                self._httpConn.waterPlantInAquaGarden(fieldID, sFields)
            nPlants = len(plants['fieldID'])
            self._logGarden.info(f'{nPlants} plants watered in the aqua garden {self._id}.')
            print(f'{nPlants} plants watered in the aqua garden {self._id}.')
        except Exception as e:
            self._logGarden.error(f'Failed to water plants in the aqua garden {self._id}. Error: {e}')



    def harvest(self):
        """Harvests everything in the aqua garden."""
        # Erntet alles im Wassergarten.

        try:
            self._httpConn.harvestAquaGarden()
        except:
            raise


    def growPlant(self, plantID, sx, sy, edge, amount):
        """Grows a water garden plant of any size and type."""
        # Отглежда водно растение във водната градина с всякакъв размер и вид.

        planted = 0
        emptyFields = self.getEmptyAquaFields()
        try:
            for field in range(1, self._MAX_FIELDS + 1):
                if planted == amount:
                    break

                fieldsToPlant = self._getAllFieldIDsFromFieldIDAndSizeAsIntList(field, sx, sy)

                if self._isPlantGrowableOnField(field, emptyFields, fieldsToPlant, edge):
                    self._httpConn.growAquaPlant(field, plantID)
                    planted += 1

                    # After planting, remove occupied fields from the list of empty fields
                    # След засаждане, премахнете заетите полета от списъка с празни полета

                    fieldsToPlantSet = set(fieldsToPlant)
                    emptyFieldsSet = set(emptyFields)
                    tmpSet = emptyFieldsSet - fieldsToPlantSet
                    emptyFields = list(tmpSet)

        except:
            self._logGarden.error('Could not plant in the aqua garden.')
            return 0
        else:
            msg = f'{planted} plants were planted in the aqua garden.'
            if emptyFields:
                msg += f' There are still {len(emptyFields)} empty fields in the aqua garden.'
            self._logGarden.info(msg)
            print(msg)
            return planted

    def removeWeed(self):
        """
        Removes all weeds, stones, and moles if sufficient money is available.
        """
        # Премахва всички плевели, камъни и кърлежи, ако има достатъчно пари.

        weedFieldsAqua = self.getWeedFields()
        freeFields = []
        for fieldID in weedFieldsAqua:
            try:
                result = self._httpConn.removeWeedOnFieldInAquaGarden(self._id, fieldID)
            except:
                self._logGarden.error(f'Field {fieldID} in AquaGarden {self._id} could not be cleared of weeds!')
            else:
                if result == 1:
                    self._logGarden.info(f'Field {fieldID} in AquaGarden {self._id} was cleared of weeds!')
                    freeFields.append(fieldID)
                else:
                    self._logGarden.error(f'Field {fieldID} in AquaGarden {self._id} could not be cleared of weeds!')

        self._logGarden.info(f'In AquaGarden {self._id}, {len(freeFields)} fields were cleared of weeds.')

