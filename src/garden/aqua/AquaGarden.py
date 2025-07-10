#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.garden.Garden import Garden
from src.garden.aqua.Http import Http

class AquaGarden(Garden):
    def __init__(self):
        Garden.__init__(self, 101)

        self.__httpAqua = Http()
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
            tmpEmptyAquaFields = self.__httpAqua.get_empty_fields()
        except Exception:
            self._logGarden.error('Konnte leere Felder von AquaGarten nicht ermitteln.')
            #BG- self._logGarden.error('Неуспешно определение на празни полета в Аква-градината.')

        else:
            return tmpEmptyAquaFields

    def water(self):
        try:
            plants = self.__httpAqua.get_plants_to_water()
            nPlants = len(plants['fieldID'])
            if nPlants and self._user.has_watering_gnome_helper():
                self.__httpAqua.water_all_plants()
            else:
                for i in range(0, nPlants):
                    sFields = self._getAllFieldIDsFromFieldIDAndSizeAsString(plants['fieldID'][i], plants['sx'][i], plants['sy'][i])
                    self.__httpAqua.water_plants(sFields)
        except Exception:
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
            self.__httpAqua.harvest()
        except Exception:
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

                if len(to_plant) == self._PLANT_PER_REQUEST or len(to_plant) + planted == amount \
                or (field == self._MAX_FIELDS and len(to_plant) > 0):
                    self.__httpAqua.grow(to_plant, plantID)
                    planted += len(to_plant)
                    to_plant = {}
                    
        except Exception:
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
                result = self.__http.remove_weed_on_field(self._id, fieldID)
            except Exception:
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
