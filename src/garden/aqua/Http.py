#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.HTTPCommunication import HTTPConnection
from src.garden.Http import Http as HttpGarden
import json, re

class Http(object):
    def __init__(self):
        self.__http: HTTPConnection = HTTPConnection()
        self.__httpGarden = HttpGarden()

    def get_empty_fields(self):
        try:
            address = f'ajax/ajax.php?do=watergardenGetGarden&token={self.__http.token()}'
            response, content = self.__http.sendRequest(address)
            self.__http.checkIfHTTPStateIsOK(response)
            jContent = self.__http.generateJSONContentAndCheckForOK(content)
            emptyAquaFields = self.__httpGarden.find_empty_fields_in_json(jContent)
        except:
            raise
        else:
            return emptyAquaFields

    def water_all_plants(self):
        """Use watering gnome to water all plants in the aquagarden (premium feature)."""
        try:
            address = f"ajax/ajax.php?do=watergardenWaterAll&token={self.__http.token()}"
            response, content = self.__http.sendRequest(address)
            self.__http.checkIfHTTPStateIsOK(response)
            self.__http.generateJSONContentAndCheckForOK(content)
        except:
            raise

    def get_plants_to_water(self):
        """
        Ermittelt alle bepflanzten Felder im Wassergartens, die auch gegossen werden können und gibt diese zurück.
        """
        try:
            response, content = self.sendRequest(f'ajax/ajax.php?do=watergardenGetGarden&token={self.__http.token()}')
            self.__http.checkIfHTTPStateIsOK(response)
            jContent = self.__http.generateJSONContentAndCheckForOK(content)
            return self.__httpGarden.find_plants_to_be_watered_in_json(jContent)
        except:
            raise

    def water_plants(self, sFieldsToWater):
        """Gießt alle Pflanzen im Wassergarten"""
        listFieldsToWater = sFieldsToWater.split(',')

        sFields = ''
        for i in listFieldsToWater:
            sFields += f'&water[]={i}'

        try:
            address = f'ajax/ajax.php?do=watergardenCache{sFields}&token={self.__http.token()}'
            response, content = self.__http.sendRequest(address)
            self.__http.checkIfHTTPStateIsOK(response)
        except:
            raise

    def harvest(self):
        """Erntet alle fertigen Pflanzen im Garten."""
        try:
            address = f'ajax/ajax.php?do=watergardenHarvestAll&token={self.__http.token()}'
            response, content = self.__http.sendRequest(address)
            jContent = json.loads(content)

            if jContent['status'] == 'error':
                print(jContent['message'])
            elif jContent['status'] == 'ok':
                msg = jContent['harvestMsg'].replace('</div>', '').replace('&nbsp;', ' ').replace('<div class="line">', '\n')
                msg = re.sub('<div.*?>', '', msg)
                msg = msg.strip()
                print(msg)
        except:
            raise

    def grow(self, to_plant, plant_id):
        """Baut eine Pflanze im Wassergarten an."""
        # address = f'ajax/ajax.php?do=watergardenCache&plant[{plant_id}]={field}&token={self.__token}' # TODO:
        address = f'ajax/ajax.php?do=watergardenCache'
        for field in to_plant.keys():
            address += f"&plant[{field}]={plant_id}" #???
        address += f"&token={self.__http.token()}"

        try:
            response, content = self.__http.sendRequest(address)
            self.__http.checkIfHTTPStateIsOK(response)
            return self.__http.generateJSONContentAndCheckForOK(content)
        except:
            raise
