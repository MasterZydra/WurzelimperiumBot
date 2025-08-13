#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.User import User
from src.garden.Http import Http
from src.logger.Logger import Logger
from src.product.ProductData import ProductData
from src.product.Products import WEEDS, TREE_STUMP, STONE, MOLE, is_booster
import i18n
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
        Logger().error(f'Unhandled plant size --> sx: {sx}, sy: {sy}')
        return None

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

    def water(self) -> bool:
        """Water all plants in the garden"""
        #BG- Градината с gardenID се полива напълно.
        Logger().info(f'Gieße alle Pflanzen im Garten {self._id}.')
        #BG- Полей всички растения в градината. {self._id}.

        plants = self.__http.get_plants_to_water(self._id)
        if plants is None:
            return False
        nPlants = len(plants['fieldID'])
        if nPlants and self._user.has_watering_gnome_helper():
            if not self.__http.water_all_plants():
                return False
        else:
            for i in range(0, nPlants):
                sFields = self._getAllFieldIDsFromFieldIDAndSizeAsString(plants['fieldID'][i], plants['sx'][i], plants['sy'][i])
                if not self.__http.water_plant(self._id, plants['fieldID'][i], sFields):
                    return False

        Logger().print(f'Im Garten {self._id} wurden {nPlants} Pflanzen gegossen.')
        #BG- В градината {self._id} са поляти {nPlants} растения.
        return True

    def get_empty_fields(self):
        """Returns all empty fields in the garden."""
        #BG- """Връща всички празни полета в градината."""
        return self.__http.get_empty_fields(self._id) or []

    def get_grown_fields(self):
        """Returns all grown fields in the garden."""
        return self.__http.get_empty_fields(self._id, param="grown") or []

    def get_weed_fields(self):
        """Returns all weed fields in the garden."""
        #BG- """Връща всички полета с плевели в градината."""
        return self.__http.get_weed_fields(self._id) or {}

    def getGrowingPlants(self):
        """Returns all growing plants in the garden."""
        #BG- """Връща всички растящи растения в градината."""
        return Counter(self.__http.get_growing_plants(self._id) or [])

    def getNextWaterHarvest(self):
        """Returns all growing plants in the garden."""
        #BG- """Връща всички растящи растения в градината."""

        overall_time = []
        Fields_data = namedtuple("Fields_data", "plant water harvest")
        max_water_time = 86400
        garden = self.__http.change_garden(self._id)
        if garden is None:
            return None
        garden = garden.get('garden')
        for field in garden.values():
            if field[0] in [WEEDS, TREE_STUMP, STONE, MOLE]:
                continue
            fields_time = Fields_data(field[10], field[4], field[3])
            if fields_time.harvest - fields_time.water > max_water_time:
                overall_time.append(fields_time.water + max_water_time)
            overall_time.append(fields_time.harvest)
        return min(overall_time)

    def harvest(self) -> bool:
        """Harvest everything"""
        #BG- """Събери всичко."""
        return self.__http.harvest(self._id)

    def harvest_unfinished(self) -> bool:
        #BG- """Отглежда растение от всякакъв размер."""

        grown_fields = self.get_grown_fields()
        Logger().debug('grown_fields:', grown_fields)

        for field, plant_id in grown_fields.items():
            sx = ProductData().get_product_by_id(plant_id).get_sx()
            if sx is None:
                return False
            sy = ProductData().get_product_by_id(plant_id).get_sy()
            if sy is None:
                return False
            fields = self._getAllFieldIDsFromFieldIDAndSizeAsString(field, sx, sy)
            if fields is None:
                return False
            if not self.__http.harvest_unfinished(plant_id, field, fields):
                return False

        return True

    def grow(self, plantID, sx, sy, amount):
        """Grows a plant of any size."""
        #BG- """Отглежда растение от всякакъв размер."""

        planted = 0
        emptyFields = self.get_empty_fields()

        to_plant = {}
        for field in range(1, self._MAX_FIELDS+1):
            
            if planted == amount: break
            fieldsToPlant = self._getAllFieldIDsFromFieldIDAndSizeAsIntList(field, sx, sy)

            if (self._isPlantGrowableOnField(field, emptyFields, fieldsToPlant, sx)):
                fields = self._getAllFieldIDsFromFieldIDAndSizeAsString(field, sx, sy) # get fields for one plant
                if fields is None:
                    return None
                to_plant.update({field: fields}) #collect all plants for a request

                #Nach dem Anbau belegte Felder aus der Liste der leeren Felder loeschen
                #BG- След отглеждането, изтрийте заетите полета от списъка на празните полета
                fieldsToPlantSet = set(fieldsToPlant)
                emptyFieldsSet = set(emptyFields)
                tmpSet = emptyFieldsSet - fieldsToPlantSet
                emptyFields = list(tmpSet)
            
            if len(to_plant) == self._PLANT_PER_REQUEST or len(to_plant) + planted == amount \
            or (field == self._MAX_FIELDS and len(to_plant) > 0):
                if self.__http.grow(to_plant, plantID, self._id) is None:
                    return None
                planted += len(to_plant)
                to_plant = {}

        Logger().print(f'Im Garten {self._id} wurden {planted} Pflanzen gepflanzt.')
        #BG- msg = f'В градината {self._id} са засадени {planted} растения.'
        if emptyFields:
            Logger().print(f'Im Garten {self._id} sind noch leere Felder vorhanden.')
            #BG- msg = msg + f' В градината {self._id} все още има празни полета.'

        return planted

    def remove_weeds(self) -> bool:
        """
        Entfernt alles Unkraut, Steine und Maulwürfe, wenn ausreichend Geld vorhanden ist.
        """
        #BG- Премахва всички плевели, камъни и кърлежи, ако има достатъчно пари.

        # Load details for all fields of this garden
        garden = self.__http.change_garden(self._id)
        if garden is None:
            return False
        garden = garden.get('garden')

        money = User().get_bar()
        weedFields = self.get_weed_fields()
        freeFields = []
        all_weeds_removed = True
        for fieldID in weedFields:
            # Check if user has enough money to pay for the removal
            field_info = garden[str(fieldID)]
            weed_type = field_info[0]
            cost_map = {WEEDS: 2.5, STONE: 50, TREE_STUMP: 250, MOLE: 500}
            cost_for_removal = cost_map.get(weed_type)

            if cost_for_removal > money:
                Logger().debug('Not enough money to remove the weeds')
                all_weeds_removed = False
                continue

            money -= cost_for_removal

            # Remove weed on field
            result = self.__http.remove_weed_on_field(self._id, fieldID)
            if result is None:
                Logger().print_error(f'Feld {fieldID} im Garten {self._id} konnte nicht von Unkraut befreit werden!')
                #BG- Полето {fieldID} в градината {self._id} не може да бъде освободено от плевели!
                return False

            if result == 1:
                Logger().print(f'Feld {fieldID} im Garten {self._id} wurde von Unkraut befreit!')
                #BG- Полето {fieldID} в градината {self._id} беше освободено от плевели!

                freeFields.append(fieldID)
            else:
                Logger().print_error(f'Feld {fieldID} im Garten {self._id} konnte nicht von Unkraut befreit werden!')
                #BG- Полето {fieldID} в градината {self._id} не може да бъде освободено от плевели!
        if all_weeds_removed:
            Logger().print(f'Im Garten {self._id} wurden {len(freeFields)} Felder von Unkraut befreit.')
            #BG- В градината {self._id} бяха освободени от плевели {len(freeFields)} полета.

        return True

    def get_fields(self):
        return self.__http.get_empty_fields(self._id, '')['garden']

    def get_booster_fields(self):
        fields = {}
        for field in self.get_fields():
            if not is_booster(self.get_fields()[field][0]):
                continue
            fields[field] = self.get_fields()[field]
        return fields