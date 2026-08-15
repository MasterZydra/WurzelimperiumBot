#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math

from src.mine.Http import Http
from src.shop.Shop import Shop

class Mine:
    """Wrapper for the Mine"""

    def __init__(self):
        self.__http = Http()
        self.__shop = Shop()
        self.__data = None
        self.update()

    def update(self):
        self.__set_data(self.__http.init())

    def __set_data(self, content):
        self.__data = content.get("data", {}).get("data", None)
        #jewel_slots = 1 immer da + freigeschaltete Schmuckhersteller-slots
        #stock = minen Lager
        #items = Lager für Acken, Dino usw.
        self.__products = content.get("data", {}).get("products", None)
        if content.get("data", {}).get("config"):
            self.__config = content.get("data", {}).get("config", None)

    def __get_mine_points(self):
        return int(self.__data.get("count", 0))

    def __get_mine_level(self) -> int:
        return int(self.__data.get("level", 0))

    def __get_product_energy(self, pid) -> int:
        return self.__products.get(pid, {}).get("energy", 999999)

    def __get_product_stock(self, pid) -> int:
        return self.__products.get(pid, {}).get("amount")

    def __get_material_stock(self, material) -> int:
        return int(self.__data.get("stock", {}).get(material, 0))
    
    def __get_worker_busy(self, worker_slot) -> int:
        return self.__data.get("worker", {}).get(worker_slot, {}).get("harvest", 1) # 1 = harvestable or while harvesting, 0 = idle

    def __get_available_workers(self) -> list:
        available_worker = []
        for worker_slot, worker_data in self.__data.get("worker", {}).items():
            if worker_data.get("harvest", 1) == 0: # 1 = harvestable or while harvesting, 0 = idle
                available_worker.append(worker_slot)
        return available_worker
    
    def __get_lowest_level_available_worker(self) -> dict:
        lowest_level_worker = {}
        for worker_slot in self.__get_available_workers():
            worker_level = self.__get_worker_level(worker_slot)
            lowest_level_worker.update({worker_slot: worker_level})

        sorted_dict = dict(sorted(lowest_level_worker.items(), key=lambda item: item[1])) 
        return sorted_dict
    
    def __get_worker_energy(self, worker_slot) -> int:
        return int(self.__data.get("worker", {}).get(worker_slot, {}).get("energy", 999))
    
    def __get_worker_level(self, worker_slot) -> int:
        return self.__data.get("worker", {}).get(worker_slot, {}).get("level", {}).get("level", 0)
    
    def __get_worker_max_energy(self, worker_level) -> int:
        return self.__config.get("worker_level", {}).get(str(worker_level), {}).get("energy", 0)
    
    def __get_material_worker_level(self, material) -> int:
        return self.__config.get("materials", {}).get(material, {}).get("worker_level", 999)
    
    def __get_material_worker_count(self, material) -> int:
        return self.__config.get("materials", {}).get(material, {}).get("worker", 999)
    
    def __get_material_energy(self, material) -> int:
        return self.__config.get("materials", {}).get(material, {}).get("energy", 999)
    
    def __get_material_category(self, material) -> int:
        return self.__config.get("materials", {}).get(material, {}).get("category", 0)
    
    def __get_item_valid(self, item_name) -> list:
        return self.__config.get("items", {}).get(item_name, {}).get("valid", [])
    
    def __get_item_material(self, item_name) -> dict:
        return self.__config.get("items", {}).get(item_name, {}).get("material", {})
    
    def __get_item_mine_points(self, item_name) -> int:
        return self.__config.get("items", {}).get(item_name, {}).get("mine_points", 0)
    
    def __check_craft_axe(self, axe_name, count):
        for material, amount in self.__get_item_material(axe_name).items():
            if not self.__get_material_stock(material) >= amount*count:
                return False
        # self.__http.craft_axe(axe_name)
        return True

    def harvest_layer(self):
        for layer, layer_data in self.__data.get("minelevels", {}).items():

            layer_slots = layer_data.get("data", {})
            for slot, slot_data in layer_slots.items():
                #nix auf Slot: name (engl.)
                #wenn gefinished: cooldown, duration, cooldown_remain
                #wenn Arbeier aktiv: name, remain--
                if slot_data.get("remain", 999999) <= 0:
                    print(f"\n HARVEST {slot}")
                    content = self.__http.finish_worker(layer, slot)
                    self.__set_data(content)

    def feed_worker(self, buy_from_shop = True):
        for worker in self.__get_available_workers():
            worker_energy = self.__get_worker_energy(worker)
            print(self.__get_worker_level(worker))
            worker_max_energy = self.__get_worker_max_energy(self.__get_worker_level(worker))

            if worker_energy < worker_max_energy: #feed
                energy_diff = worker_max_energy - worker_energy
                #TODO: pid, amount = self.__get_refill_product(energy_diff)
                pid = "4"
                print(self.__get_product_energy(pid))
                amount = math.ceil(energy_diff/self.__get_product_energy(pid))
                print(self.__get_product_stock(pid))
                if not amount >= self.__get_product_stock(pid): #zu wenig Produkte auf Lager
                    if not buy_from_shop:
                        return False
                    self.__shop.buy(product_name=int(pid), amount=amount)
                self.__shop.buy(product_name=2, amount=1)
                content = self.__http.refill_worker_energy(worker, pid, amount)
                self.__set_data(content)

    def start_worker(self, dino_active, dino_fav):
        # suche items die auf ebenen sind oder suche höchste items ob auf ebenen vorhanden?!
        #prio: edelsteine, wenn nix, dann Erz?

        #Strat
            #bei höchster Ebene beginne, suchen bis Edelstein oder Erz gefunden mit hohem Level
            #innerhalb selben level: erst Edel, dann Erz
            #chekc workercount --> wenn zu hoch --> level niedriger

        for worker_slot, worker_level in self.__get_lowest_level_available_worker().items():
            amount_available_worker = len(self.__get_available_workers())
            if self.__get_worker_busy(worker_slot):
                continue
            
            potential_slot = {"layer": 0, "slot": 0, "material": 0, "worker_level": 0, "category": 0, "axe": 0}

            sorted_dict = dict(sorted(self.__data.get("minelevels", {}).items(), key=lambda item: int(item[0]), reverse=True))  
            for layer, layer_data in sorted_dict.items():
                layer_slots = layer_data.get("data", {})
                for slot, slot_data in layer_slots.items():
                    #nix auf Slot: name (engl.)
                    #wenn gefinished: cooldown, duration, cooldown_remain
                    #wenn Arbeier aktiv: name, remain--
                    if slot_data.get("duration", 0): #Slot hat cooldown oder wird bereits bearbeitet
                        continue

                    slot_material = slot_data.get("name", None)
                    if worker_level < self.__get_material_worker_level(slot_material):
                        continue
                    if amount_available_worker < self.__get_material_worker_count(slot_material):
                        continue
                    #TODO: necessary?: if self.__get_material_energy(slot_material) > self.__get_worker_energy(worker_slot)

                    #worker_level >=
                    if self.__get_material_worker_level(slot_material) == potential_slot.get("worker_level"):
                        if not self.__get_material_category(slot_material) > potential_slot.get("category"): #category 1=Erz, 2=Edelstein (Prio)
                            continue
                    elif not self.__get_material_worker_level(slot_material) > potential_slot.get("worker_level"):
                        continue

                    #check if axes available, craftable
                    possible_axes = ["stonepickaxe","brasspickaxe","bronzepickaxe","steelpickaxe"] #except "ironpickaxe"
                    best_axe = None
                    for axe in possible_axes:
                        valid_material = self.__get_item_valid(axe)
                        if not slot_material in valid_material:
                            continue
                        #if in stock or craftable
                        axe_id = []
                        needed_amount = self.__get_material_worker_count(slot_material)

                        for item_id, item_data in self.__data.get("items", {}).items():
                            if not item_data.get("instock", "0") == "1":
                                continue
                            if item_data.get("name", "") == axe:
                                axe_id.append(item_id)
                        if len(axe_id) < needed_amount:
                            for i in range (needed_amount - len(axe_id)):
                                if not self.__check_craft_axe(axe, needed_amount - len(axe_id)): break

                        best_axe = axe
                        break
                    if not best_axe: continue

                    potential_slot = {"layer": layer, "slot": slot, "material": slot_material, "worker_level": self.__get_material_worker_level(slot_material), "category": self.__get_material_category(slot_material), "axe": best_axe}
            
            worker = '' #{"1":3,"2":6}
            for i in range(1, self.__get_material_worker_count(potential_slot.get("material"))+1):
                worker = worker + f'"{i}":{int(list(self.__get_lowest_level_available_worker().keys())[i-1])},'
            worker = worker[:-1]

            items = '' #{"1":171447,"2":171450}
            for i in range(1, self.__get_material_worker_count(potential_slot.get("material"))+1):
                items = items + f'"{i}":{int( self.__craft_axe(potential_slot.get("axe"), count=self.__get_material_worker_count(potential_slot.get("material")))[i-1] )},'
            items = items[:-1]
            
            favdino = f"dino{dino_fav}"
            setup = f'"level":{potential_slot.get("layer")},"pos":{potential_slot.get("slot")},"favdino":"{favdino}","worker":{{{worker}}},"items":{{{items}}}'
            #ohne Dino: setup={"level":2,"pos":1,"favdino":"dino2","worker":{"1":1},"items":{"1":179977}}

            ##DINO
            if dino_active and self.__get_mine_level() >= 5:
                print("get dino item")
                if self.__craft_dino_item("dinoitem1"):
                    item1 = self.__craft_dino_item("dinoitem1") #150 mine_points
                    item2 = self.__craft_dino_item("dinoitem6")
                    if self.__craft_dino_item("dinoitem7"): #"dinoitem7" 1200 mine_points --> fallback "dinoitem6"
                        item2 = self.__craft_dino_item("dinoitem7")
                    setup = setup + f',"dinos":{{"1":{item1},"2":{item2}}}'

            content = self.__http.start_worker(setup)
            self.__set_data(content)

    def __craft_dino_item(self, item_name) -> int:
        items = []

        for item_id, item_data in self.__data.get("items", {}).items():
            if not item_data.get("instock", "0") == "1":
                continue
            if item_data.get("name", "") == item_name:
                items.append(item_id)

        if not len(items) > 0:
            if not self.__get_item_mine_points(item_name) <= self.__get_mine_points():
                return 0
            content = self.__http.craft_item(item_name)
            self.__set_data(content)
            items.append(list(self.__data.get("items", {}).values())[-1])

        return items[0]
    
    def __craft_axe(self, axe_name, count = 1) -> list:
        axe_id = []

        for item_id, item_data in self.__data.get("items", {}).items():
            if not item_data.get("instock", "0") == "1":
                continue
            if item_data.get("name", "") == axe_name:
                axe_id.append(item_id)
        if len(axe_id) < count:
            for i in range (count - len(axe_id)):
                if not self.__check_craft_axe(axe_name, count - len(axe_id)): return []
                content = self.__http.craft_item(axe_name)
                self.__set_data(content)
                axe_id.append(list(self.__data.get("items", {}).keys())[-1])
        if len(axe_id) < count: return []

        return axe_id
