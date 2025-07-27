#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.HTTPCommunication import HTTPConnection
from src.logger.Logger import Logger
from src.product.Products import WEEDS, TREE_STUMP, STONE, MOLE
import json, re, time

class Http:
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()

    def get_plants_to_water(self, gardenID):
        """
        Ermittelt alle bepflanzten Felder im Garten mit der Nummer gardenID,
        die auch gegossen werden können und gibt diese zurück.
        """
        try:
            address = f'ajax/ajax.php?do=changeGarden&garden={str(gardenID)}&token={self.__http.token()}'
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            jContent = self.__http.get_json_and_check_for_ok(content)
            return self.find_plants_to_be_watered_in_json(jContent)
        except Exception:
            Logger().print_exception('Failed to get plants to water in garden')
            return None

    def water_all_plants(self) -> bool:
        """Use watering gnome to water all plants in a garden (premium feature)."""
        try:
            address = f"ajax/ajax.php?do=gardenWaterAll&token={self.__http.token()}"
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            self.__http.get_json_and_check_for_ok(content)
            return True
        except Exception:
            Logger().print_exception('Failed to water plants in garden')
            return False

    def water_plant(self, iGarten, iField, sFieldsToWater) -> bool:
        """Bewässert die Pflanze iField mit der Größe sSize im Garten iGarten."""
        try:
            address =   f'save/wasser.php?feld[]={str(iField)}&felder[]={sFieldsToWater}' \
                        f'&cid={self.__http.token()}&garden={str(iGarten)}'
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            self.__http.get_yaml_and_check_for_success(content.decode('UTF-8'))
            return True
        except Exception:
            Logger().print_exception('Failed to water plant in garden')
            return False

    def get_empty_fields(self, gardenID, param="empty"):
        """Gibt alle leeren Felder eines Gartens zurück."""
        try:
            address = f'ajax/ajax.php?do=changeGarden&garden={str(gardenID)}&token={self.__http.token()}'
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            jContent = self.__http.get_json_and_check_for_ok(content)
            if param == "empty":
                return self.find_empty_fields_in_json(jContent)
            elif param == "grown":
                return self.__find_grown_fields(jContent)
            return jContent
        except Exception:
            Logger().print_exception('Failed to get empty fields in garden')
            return None

    def __find_grown_fields(self, jContent):
        """Sucht im JSON Content nach Felder die bepflanzt sind und gibt diese zurück."""
        grown_fields = {}
        for index in jContent['grow']:
            field = index[0]
            plant_id = index[1]
            grown_fields.update({field: plant_id})

        return grown_fields

    def get_weed_fields(self, gardenID):
        """Gibt alle Unkraut-Felder eines Gartens zurück."""
        try:
            address = f'ajax/ajax.php?do=changeGarden&garden={str(gardenID)}&token={self.__http.token()}'
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            jContent = self.__http.get_json_and_check_for_ok(content)
            return self.__find_weed_fields_in_json(jContent)
        except Exception:
            Logger().print_exception('Failed to get weed fields in garden')
            return None

    def __find_weed_fields_in_json(self, jContent):
        """Sucht im JSON Content nach Felder die mit Unkraut befallen sind und gibt diese zurück."""
        weedFields = {}

        for field in jContent['garden']:
            if jContent['garden'][field][0] in [WEEDS, TREE_STUMP, STONE, MOLE]:
                weedFields[int(field)] = float(jContent['garden'][field][6])

        #Sortierung über ein leeres Array ändert Objekttyp zu None
        if len(weedFields) > 0:
            weedFields = {key: value for key, value in sorted(weedFields.items(), key=lambda item: item[1])}

        return weedFields

    def get_growing_plants(self, gardenID):
        """Returns all fields with growing plants of a garden."""
        try:
            address = f'ajax/ajax.php?do=changeGarden&garden={str(gardenID)}&token={self.__http.token()}'
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            jContent = self.__http.get_json_and_check_for_ok(content)
            return self.__find_growing_plants_in_json(jContent)
        except Exception:
            Logger().print_exception('Failed to get growing plants in garden')
            return None

    def __find_growing_plants_in_json(self, jContent):
        """Returns list of growing plants from JSON content"""
        growingPlants = []
        for field in jContent['grow']:
            growingPlants.append(field[1])
        return growingPlants

    def harvest(self, gardenID) -> bool:
        """Erntet alle fertigen Pflanzen im Garten."""
        try:
            if self.change_garden(gardenID) is None:
                return False
            address = f'ajax/ajax.php?do=gardenHarvestAll&token={self.__http.token()}'
            response, content = self.__http.send(address)
            jContent = json.loads(content)

            if jContent['status'] == 'error':
                Logger().print(jContent['message'])
            elif jContent['status'] == 'ok':
                msg = jContent['harvestMsg'].replace('</div>', '').replace('&nbsp;', ' ').replace('<div class="line">', '\n')
                msg = re.sub('<div.*?>', '', msg)
                msg = msg.strip()
                if 'biogas' in jContent:
                    biogas = jContent['biogas']
                    msg = msg + f"\n{biogas} Gartenabfälle"
                if 'eventitems' in jContent:
                    eventitems = jContent['collectevent']
                    msg = msg + f"\n{eventitems} Eventitems" #TODO check which event is active
                Logger().print(msg)
            return True
        except Exception:
            Logger().print_exception(f'Failed to harvest in garden {gardenID}')
            return False

    def harvest_unfinished(self, plant_id, field, fields) -> bool:
        try:
            address = f"save/ernte.php?pflanze[]={plant_id}&feld[]={field}&felder[]={fields}&closepopup=1&ernteJa=ernteJa"
            self.__http.send(address)
            return True
        except Exception:
            Logger().print_exception('Failed to harvest unfinished plants')
            return False

    def grow(self, to_plant, plant_id, gardenID):
        """Baut eine Pflanze auf einem Feld an."""
        address =   f"save/pflanz.php?pflanze[]={plant_id}"
        for count in range (len(to_plant)-1):
            address += f"&pflanze[]={plant_id}"
        for field in to_plant.keys():
            address += f"&feld[]={field}" #???
        for fields in to_plant.values():
            address += f"&felder[]={fields}" #???
        address += f"&cid={self.__http.token()}&garden={gardenID}"
        try:
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_success(content)
        except Exception:
            Logger().print_exception(f'Failed to grow plant {plant_id} in garden {gardenID}')
            return None

    def remove_weed_on_field(self, gardenID, fieldID):
        """Befreit ein Feld im Garten von Unkraut."""
        if self.change_garden(gardenID) is None:
            return None

        try:
            response, content = self.__http.send(f'save/abriss.php?tile={fieldID}', 'POST')
            self.__http.check_http_state_ok(response)
            jContent = self.__http.get_json_and_check_for_success(content)
            return jContent['success']
        except Exception:
            Logger().print_exception(f'Failed to remove weed from field {fieldID} in garden {gardenID}')
            return None

    def change_garden(self, gardenID):
        """Wechselt den Garten."""
        try:
            address = f'ajax/ajax.php?do=changeGarden&garden={str(gardenID)}&token={self.__http.token()}'
            response, content = self.__http.send(address)
            self.__http.check_http_state_ok(response)
            return self.__http.get_json_and_check_for_ok(content)
        except Exception:
            Logger().print_exception(f'Failed to change to garden {gardenID}')
            return None

    def find_plants_to_be_watered_in_json(self, jContent):
        """Sucht im JSON Content nach Pflanzen die bewässert werden können und gibt diese inkl. der Pflanzengröße zurück."""
        plantsToBeWatered = {'fieldID': [], 'sx': [], 'sy': []}
        for field in range(0, len(jContent['grow'])):
            plantedFieldID = jContent['grow'][field][0]
            plantSize = jContent['garden'][str(plantedFieldID)][9]
            splittedPlantSize = str(plantSize).split('x')
            sx = splittedPlantSize[0]
            sy = splittedPlantSize[1]

            if not self.is_field_watered(jContent, plantedFieldID):
                fieldIDToBeWatered = plantedFieldID
                plantsToBeWatered['fieldID'].append(fieldIDToBeWatered)
                plantsToBeWatered['sx'].append(int(sx))
                plantsToBeWatered['sy'].append(int(sy))

        return plantsToBeWatered

    def is_field_watered(self, jContent, fieldID):
        """
        Ermittelt, ob ein Feld fieldID gegossen ist und gibt True/False zurück.
        Ist das Datum der Bewässerung 0, wurde das Feld noch nie gegossen.
        Eine Bewässerung hält 24 Stunden an. Liegt die Zeit der letzten Bewässerung
        also 24 Stunden + 30 Sekunden (Sicherheit) zurück, wurde das Feld zwar bereits gegossen,
        kann jedoch wieder gegossen werden.
        """
        oneDayInSeconds = (24*60*60) + 30
        currentTimeInSeconds = time.time()
        waterDateInSeconds = int(jContent['water'][fieldID-1][1])

        if waterDateInSeconds == '0' or (currentTimeInSeconds - waterDateInSeconds) > oneDayInSeconds:
            return False
        else:
            return True

    def find_empty_fields_in_json(self, jContent):
        """Sucht im JSON Content nach Felder die leer sind und gibt diese zurück."""
        emptyFields = []

        for field in jContent['garden']:
            if jContent['garden'][field][0] == 0:
                emptyFields.append(int(field))

        #Sortierung über ein leeres Array ändert Objekttyp zu None
        if len(emptyFields) > 0:
            emptyFields.sort(reverse=False)

        return emptyFields
