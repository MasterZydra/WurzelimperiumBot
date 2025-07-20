#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.garden.Garden import Garden
from src.garden.herb.Http import Http
from src.logger.Logger import Logger
from src.product.ProductData import ProductData
from src.shop.Shop import Shop
from src.stock.Stock import Stock

class HerbGarden(Garden):
    def __init__(self):
        Garden.__init__(self, 201)

        self.__httpHerb = Http()
        self.__setValidFields()
        self.__jContent = self.__httpHerb.load_data()
        self.__exchange = self.__jContent['exchange']
        self.__setHerbGardenInfo(self.__jContent)

    def __setValidFields(self):
        self._VALID_FIELDS = {}
        for x in range(1, 205, 34):
            for y in range(x, x+7, 2):
                self._VALID_FIELDS.update({y: self._getAllFieldIDsFromFieldIDAndSizeAsString(y, 2, 2)})

    def __setHerbGardenInfo(self, jContent) -> bool:
        if jContent is None:
            return False
        self.__jContent = jContent
        self.__info = self.__jContent['info']
        self.__weed = self.__jContent['weed']
        return True

    def _isPlantGrowableOnField(self, fieldID, emptyFields):
        """Prüft anhand mehrerer Kriterien, ob ein Anpflanzen möglich ist."""
        # Betrachtetes Feld darf nicht besetzt sein
        if not (fieldID in emptyFields): return False
        return True

    def harvest(self) -> bool:
        # TODO: proof if any harvestable
        jContent = self.__httpHerb.harvest()
        if jContent is None:
            return False
        if jContent['status'] == 'error':
            msg = jContent['message']
        elif jContent['status'] == 'ok':
            msg = jContent['harvestMsg']
            self.__setHerbGardenInfo(jContent)
        Logger().print(msg)
        return True

    def remove_weeds(self) -> bool:
        #Abfrage if jContent['weed']
        # msg = "In deinem Kräutergarten ist kein Unkraut."
        # if self.__weed:
        jContent = self.__httpHerb.remove_weed()
        if jContent is None:
            return False
        msg = jContent.get('message', None)
        self.__setHerbGardenInfo(jContent)
        Logger().print(msg)
        return True

    def get_empty_fields(self):
        """Sucht im JSON Content nach Felder die leer sind und gibt diese zurück."""
        emptyFields = []
        for field in self.__jContent['garden']:
            if self.__jContent['garden'][field][0] == 0 and int(field) in self._VALID_FIELDS.keys():
                emptyFields.append(int(field))

        #Sortierung über ein leeres Array ändert Objekttyp zu None
        if len(emptyFields) > 0:
            emptyFields.sort(reverse=False)

        return emptyFields

    def grow_plant(self, amount=24):
        """Grows a plant of any size."""
        herbID = self.__info.get('herbid')
        herb_stock = Stock().get_stock_by_product_id(herbID)

        if not self.__info.get('canPlant'):
            return 0
        
        if self.__info.get('send') >= self.__info.get('amount'):
            return 0

        while not herb_stock >= amount:
            self.exchange()
            herb_stock = Stock().get_stock_by_product_id(herbID)
        
        planted = 0
        emptyFields = self.get_empty_fields()
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

                if len(to_plant) == self._PLANT_PER_REQUEST or len(to_plant) + planted == amount \
                or (field == self._MAX_FIELDS and len(to_plant) > 0):
                    self.__http.grow(to_plant, herbID, self._id)
                    planted += len(to_plant)
                    to_plant = {}
                    
            Logger().print(f'Im Garten {self._id} wurden {planted} Pflanzen gepflanzt.')
            if emptyFields: 
                Logger().print(f'Im Garten {self._id} sind noch leere Felder vorhanden.')
            return planted
        except Exception:
            Logger().print_error(f'Im Garten {self._id} konnte nicht gepflanzt werden.')
            return None

    def exchange(self) -> bool:
        exchange = {}
        buy_price = {}

        for plant in self.__exchange:
            pid = plant['plant']
            amount = plant['amount']
            exchange.update({pid: amount})
            total = amount * ProductData().get_product_by_id(pid).get_price_npc()
            buy_price.update({pid: total})

        sorted_dict = sorted(buy_price.items(), key=lambda x:x[1])
        cheapest_plant = next(iter(sorted_dict))[0]

        stock = Stock().get_stock_by_product_id(cheapest_plant)
        amount = exchange[cheapest_plant]

        if not stock >= amount:
            if not Shop().buy(ProductData().get_product_by_id(cheapest_plant).get_name(), amount):
                return False

        if not self.__httpHerb.exchange(cheapest_plant):
            return False

        return Stock().update()