#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.User import User
from src.garden.Http import Http
from src.product.ProductData import ProductData
import i18n, logging
from collections import Counter, namedtuple

i18n.load_path.append('lang')

class Garden:
    _LEN_X = 17
    _LEN_Y = 12
    _MAX_FIELDS = _LEN_X * _LEN_Y
    _PLANT_PER_REQUEST = 6

    def __init__(self, gardenID):
        self._id = gardenID
        self.__http = Http()
        self._user = User()
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
            plants = self.__http.get_plants_to_water(self._id)
            nPlants = len(plants['fieldID'])
            if nPlants and self._user.has_watering_gnome_helper():
                self.__http.water_all_plants()
            else:
                for i in range(0, nPlants):
                    sFields = self._getAllFieldIDsFromFieldIDAndSizeAsString(plants['fieldID'][i], plants['sx'][i], plants['sy'][i])
                    self.__http.water_plant(self._id, plants['fieldID'][i], sFields)
        except Exception:
            self._logGarden.error(f'Garten {self._id} konnte nicht bewässert werden.')
            #BG- self._logGarden.error(f'Градина {self._id} не може да бъде поливана.')
        else:
            self._logGarden.info(f'Im Garten {self._id} wurden {nPlants} Pflanzen gegossen.')
            #BG-self._logGarden.info(f'В градината {self._id} са поляти {nPlants} растения.')

            print(f'Im Garten {self._id} wurden {nPlants} Pflanzen gegossen.')
            #BG- print(f'В градината {self._id} са поляти {nPlants} растения.')

    def get_empty_fields(self):
        """Returns all empty fields in the garden."""
        #BG- """Връща всички празни полета в градината."""
        try:
            return self.__http.get_empty_fields(self._id)
        except Exception:
            self._logGarden.error(f'Konnte leere Felder von Garten {self._id} nicht ermitteln.')
            #BG- self._logGarden.error(f'Неуспешно определение на празни полета в градина {self._id}.')

    def get_grown_fields(self):
        """Returns all grown fields in the garden."""
        try:
            return self.__http.get_empty_fields(self._id, param="grown")
        except Exception:
            self._logGarden.error(f'Konnte bepflanzte Felder von Garten {self._id} nicht ermitteln.')
            #BG- self._logGarden.error(f'Неуспешно определение на празни полета в градина {self._id}.')

    def getWeedFields(self):
        """Returns all weed fields in the garden."""
        #BG- """Връща всички полета с плевели в градината."""
        try:
            return self.__http.get_weed_fields(self._id)
        except Exception:
            self._logGarden.error(f'Konnte Unkraut-Felder von Garten {self._id} nicht ermitteln.')
            #BG- self._logGarden.error(f'Неуспешно определение на полета с плевели в градина {self._id}.')

    def getGrowingPlants(self):
        """Returns all growing plants in the garden."""
        #BG- """Връща всички растящи растения в градината."""

        try:
            return Counter(self.__http.get_growing_plants(self._id))
        except Exception:
            self._logGarden.error('Could not determine growing plants of garden ' + str(self._id) + '.')
            #BG- self._logGarden.error('Неуспешно определение на растящите растения в градина ' + str(self._id) + '.')

    def getNextWaterHarvest(self):
        """Returns all growing plants in the garden."""
        #BG- """Връща всички растящи растения в градината."""

        overall_time = []
        Fields_data = namedtuple("Fields_data", "plant water harvest")
        max_water_time = 86400
        try:
            garden = self.__http.change_garden(self._id).get('garden')
            for field in garden.values():
                if field[0] in [41, 42, 43, 45]:
                    continue
                fields_time = Fields_data(field[10], field[4], field[3])
                if fields_time.harvest - fields_time.water > max_water_time:
                    overall_time.append(fields_time.water + max_water_time)
                overall_time.append(fields_time.harvest)
            return min(overall_time)
        except Exception:
            self._logGarden.error('Could not determine growing plants of garden ' + str(self._id) + '.')
            #BG- self._logGarden.error('Неуспешно определение на растящите растения в градина ' + str(self._id) + '.')

    def harvest(self):
        """Harvest everything"""
        #BG- """Събери всичко."""

        try:
            self.__http.harvest(self._id)
        except Exception:
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
                self.__http.harvest_unfinished(plant_id, field, fields)
        except Exception:
            raise

    def grow(self, plantID, sx, sy, amount):
        """Grows a plant of any size."""
        #BG- """Отглежда растение от всякакъв размер."""

        planted = 0
        emptyFields = self.get_empty_fields()

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
                
                if len(to_plant) == self._PLANT_PER_REQUEST or len(to_plant) + planted == amount \
                or (field == self._MAX_FIELDS and len(to_plant) > 0):
                    self.__http.grow(to_plant, plantID, self._id)
                    planted += len(to_plant)
                    to_plant = {}

        except Exception:
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
                result = self.__http.remove_weed_on_field(self._id, fieldID)
            except Exception:
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
