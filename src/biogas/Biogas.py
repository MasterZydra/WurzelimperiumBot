#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import math
from random import shuffle
from collections import Counter

from src.core.User import User
from src.biogas.Http import Http
from src.biogas.Stocks import Stocks
from src.logger.Logger import Logger
from src.product.Product import Product
from src.product.ProductData import ProductData

class Biogas:
    """All important information for the recycling center."""

    def __init__(self):
        self.__http = Http()
        self.__user = User()
        self.__data = {}
        self.__bonus = 0
        self.__items = {"compost": "shovel3", "muck": "mixer3", "fermenter": "fork2", "powerhouse": "manual3"}
        self.update()

        self.__set_targets()

    def update(self) -> bool:
        self.__set_data(self.__http.get_recycling_center_info())
        self.__bonus = int(self.__data.get("lastquest", 0))*0.15 #+15% bonus for each finished quest
        print('➡ src/biogas/Biogas.py:31 self.__bonus:', self.__bonus)

    def __set_targets(self): #wenn target, skip production von diesem
        self.__stock_targets = {}
        self.__stock_targets.update({"soil1": self.__get_stock_capacity("compost") * 0.35})
        self.__stock_targets.update({"soil2": self.__get_stock_capacity("compost") * 0.2})
        self.__stock_targets.update({"soil3": self.__get_stock_capacity("compost") * 0.15})
        self.__stock_targets.update({"soil4": self.__get_stock_capacity("compost") * 0.08})
        self.__stock_targets.update({"soil5": self.__get_stock_capacity("compost") * 0.05})
        self.__stock_targets.update({"fertilizer1": self.__get_stock_capacity("muck") * 0.35})
        self.__stock_targets.update({"fertilizer2": self.__get_stock_capacity("muck") * 0.2})
        self.__stock_targets.update({"fertilizer3": self.__get_stock_capacity("muck") * 0.15})
        self.__stock_targets.update({"fertilizer4": self.__get_stock_capacity("muck") * 0.08})
        self.__stock_targets.update({"fertilizer5": self.__get_stock_capacity("muck") * 0.05})
        self.__stock_targets.update({"gas": self.__get_stock_capacity("fermenter") * 0.25})
        self.__stock_targets.update({"energy": self.__get_stock_capacity("energy") * 0.25})
        self.__stock_targets.update({"heat": self.__get_stock_capacity("powerhouse") * 0.25})

        print('➡ src/biogas/Biogas.py:48 self.__stock_targets:', self.__stock_targets)

    def __get_target_stock(self, material):
        return self.__stock_targets.get(material, 0)

    def sell_to_wimp(self, slot) -> bool:
        data = self.__http.sell_to_wimp(slot)
        if data is None:
            return False

        wimp_rubbish = self.__get_wimps_data().get("1").get("data").get("rubbish")
        Logger().print(f"Sold {wimp_rubbish} rubbish.")
        return self.__set_data(data)

    def calculate_rubbish(self, plants: Counter):
        # formula: 4 / Anz. Gärten / 24 x Felder x Wachstumsdauer (Original in Std.) x 1+Bonus 
        # Wenn mehrere verschiedene Pflanzen gleichzeitig geerntet werden, wird die Berechnung für jede Pflanze separat durchgeführt und dann gerundet.
#         Am Ende werden die gerundeten Werte addiert.
        rubbish = 0

        # sum of harvestable plants as input
        for plant, plant_count in plants.items():
            Logger().print(f'➡ src/biogas/Biogas.py:38 plant: {plant}')
            Logger().print(f'➡ src/biogas/Biogas.py:38 plant_count: {plant_count}')
            product: Product = ProductData().get_product_by_id(plant)
            rubbish += 4/self.__user.get_number_of_gardens()/24*product.get_sx()*product.get_sy()*int(plant_count)*product.get_growing_time()/3600*(1+self.__bonus)
            Logger().print(f'➡ src/biogas/Biogas.py:40 rubbish_biogas: {rubbish}')
        rubbish_rounded = math.floor(rubbish + 0.5) / 1 # round_half_up
        Logger().print(f'➡ src/biogas/Biogas.py:59 rubbish_rounded: {rubbish_rounded}')
        rubbish_rounded_py = round(rubbish)
        Logger().print(f'➡ src/biogas/Biogas.py:59 rubbish_rounded_py: {rubbish_rounded_py}')
        return rubbish_rounded

    def check_rubbish_capacity(self, rubbish_to_add) -> bool:
        self.update()
        rubbish_stock = float(self.__get_stock().get("rubbish"))
        Logger().print(f'➡ src/biogas/Biogas.py:65 rubbish_stock: {rubbish_stock}')
        return rubbish_to_add + rubbish_stock < self.__get_stock_capacity(Stocks.RUBBISH)

    def harvest_productions(self):
        if self.__data.get("productions", 0):
            for production_area, production_slots in self.__data.get("productions", {}).items():
                print('➡ src/biogas/Biogas.py:94 production_area:', production_area)
                for production_slot, production_data in production_slots.items():
                    print('➡ src/biogas/Biogas.py:97 production_slot:', production_slot)
                    print('➡ src/biogas/Biogas.py:97 production_data:', production_data)
                    if production_data.get("remain", 999999) <= 0:
                        print(f"\n HARVEST {production_area} {production_slot}")
                        content = self.__http.harvest_production(production_area, production_slot)
                        self.__set_data(content)

    def start_worker(self):
        for worker in self.__get_available_worker():
            print("\n\n")
            print('➡ src/mine/Mine.py:121 worker:', worker)
            amount_available_worker = len(self.__get_available_worker())
            print('➡ src/mine/Mine.py:125 amount_available_worker:', amount_available_worker)

            if self.__get_worker_busy(worker):
                print("EXIT 1")
                continue
            dict_as_list_of_entries = [*self.__config.get("materials", {}).items()]
            print('➡ src/biogas/Biogas.py:156 dict_as_list_of_entries:', dict_as_list_of_entries)
            dict_as_list_of_entries.pop(0)
            print('➡ src/biogas/Biogas.py:154 dict_as_list_of_entries:', dict_as_list_of_entries)
            shuffle(dict_as_list_of_entries)
            print('➡ src/biogas/Biogas.py:156 dict_as_list_of_entries:', dict_as_list_of_entries)
            for material, material_data in dict_as_list_of_entries:
                print('➡ src/biogas/Biogas.py:158 material_data:', material_data)
                print('➡ src/biogas/Biogas.py:155 material:', material)

                
                if self.__get_material_stock(material) >= self.__get_target_stock(material):
                    print("EXIT 2")
                    continue

                production_area = material_data.get("category", None)
                print('➡ src/biogas/Biogas.py:170 production_area:', production_area)
                free_slots = self.__get_free_production_area_slots(production_area)
                if not len(free_slots) > 0:
                    print("EXIT 3")
                    continue
                
                selected_size = 0
                for size, material_needs in self.__config.get("productions", {}).get(material, {}).items():
                    print('➡ src/biogas/Biogas.py:178 size:', size)
                    print('➡ src/biogas/Biogas.py:178 material_needs:', material_needs)
                    worker_needed = material_needs.get("worker", 999)
                    print('➡ src/biogas/Biogas.py:181 worker_needed:', worker_needed)
                    free_stock_space = self.__get_free_stock_space(production_area)
                    print('➡ src/biogas/Biogas.py:183 free_stock_space:', free_stock_space)
                    print('➡ src/biogas/Biogas.py:186 free_stock_space:', free_stock_space)
                    print('➡ src/biogas/Biogas.py:186 material_needs.get("amount":', material_needs.get("amount"))
                    print('➡ src/biogas/Biogas.py:186 amount_available_worker:', amount_available_worker)
                    print('➡ src/biogas/Biogas.py:186 worker_needed:', worker_needed)
                    if worker_needed > amount_available_worker or material_needs.get("amount", 999999) > free_stock_space:
                        print("EXIT 4")
                        continue
                    selected_size = size
                    selected_worker_needed = worker_needed
                    print('➡ src/biogas/Biogas.py:188 selected_size:', selected_size)
                print('➡ src/biogas/Biogas.py:169 selected_size:', selected_size)

                #TODO: check if rubbish to craft is enough

                if not selected_size:
                    print("EXIT 5")
                    continue

                worker = '' #{"1":3,"2":6}
                for i in range(1, selected_worker_needed+1):
                    print('➡ src/biogas/Biogas.py:205 i:', i)
                    worker = worker + f'"{i}":{int(self.__get_available_worker()[i-1])},'
                worker = worker[:-1] #remove last comma
                print('➡ src/mine/Mine.py:229 worker:', worker)

                items = '' #{"1":171447,"2":171450}
                for i in range(1, selected_worker_needed+1):
                    items = items + f'"{i}":{int(self.__select_items(self.__items.get(production_area), count=selected_worker_needed)[i-1])},'
                    print('➡ src/mine/Mine.py:172 items:', items)
                items = items[:-1] #remove last comma
                print('➡ src/mine/Mine.py:229 items:', items)
                
                setup = f'"{production_area}":{{"slot":{free_slots[0]},"pid":"{material}","package":{selected_size},"worker":{{{worker}}},"items":{{{items}}}}}'
                print('➡ src/biogas/Biogas.py:178 setup:', setup)
                content = self.__http.start_production(setup)
                self.__set_data(content)
                break
    # Internal helper functions

    def __set_data(self, content):
        if content is None:
            return False
        self.__data = content.get("data", {}).get("data", {})
        if content.get("data", {}).get("config", {}):
            self.__config = content.get("data", {}).get("config", {})
        return True

    def __get_wimps_data(self) -> dict:
        return self.__data.get("customers", {})

    def __get_stock(self) -> dict:
        return self.__data.get("stock", {})

    def __get_free_stock_space(self, production_area):
        free = 0
        if production_area == "rubbish":
            free = self.__get_stock_capacity(production_area) - self.__get_material_stock("rubbish")
        elif production_area == "compost":
            compost_stock = 0
            for i in range(1, 6):
                compost_stock = compost_stock + self.__get_material_stock(f"soil{i}")
            free = self.__get_stock_capacity(production_area) - compost_stock
        elif production_area == "muck":
            muck_stock = 0
            for i in range(1, 6):
                muck_stock = muck_stock + self.__get_material_stock(f"fertilizer{i}")
            free = self.__get_stock_capacity(production_area) - muck_stock
        elif production_area == "fermenter":
            free = self.__get_stock_capacity(production_area) - self.__get_material_stock("biogas")
        elif production_area == "powerhouse": #contains resources: energy & powerhouse/heat
            powerhouse_stock = 0
            powerhouse_stock = self.__get_material_stock("energy") + self.__get_material_stock("heat")
            free = self.__get_stock_capacity(production_area) + self.__get_stock_capacity("energy") - powerhouse_stock
        return free

    def __get_material_stock(self, material) -> int:
        return int(self.__get_stock().get(material, -1))
    
    def __get_material_area(self, material) -> str:
        return self.__config.get("prodcutions", {}).get(material, {}).get

    def __get_stock_level(self, stock_type) -> int:
        # rubbish, compost, muck, fermenter, energy, powerhouse
        return self.__data.get("stock_level", {}).get(stock_type, -1)
    
    def __get_recycling_center_level(self):
        return self.__data.get("level", -1)

    def __get_stock_capacity(self, stock) -> int:
        config = self.__config.get("stock_level", {}).get(stock, 0)
        stock_level = self.__data.get("stock_level", {}).get(stock, 0)
        return config.get(str(stock_level), {}).get("capacity", 0)
    
    def __get_available_worker(self) -> list: #ODER über data-worker-productionid
        unlocked_worker = list(self.__data.get("worker", {}).keys())
        unlocked_worker = {int(v) if v.isnumeric() else v for v in self.__data.get("worker", {}).keys()}
        # print('➡ src/biogas/Biogas.py:147 unlocked_worker:', unlocked_worker)
        busy_worker = []
        
        available_worker = unlocked_worker
        if self.__data.get("productions", 0):
            for production_area, production_slots in self.__data.get("productions", {}).items():
                for production_slot, production_data in production_slots.items():
                    if production_data.get("data", {}).get("worker", {}):
                        production_area_worker = list(production_data.get("data", {}).get("worker", {}).values())
                        busy_worker = busy_worker + production_area_worker
        available_worker = [x for x in unlocked_worker if x not in busy_worker]
        
        rent_worker = []
        for worker_slot, worker_data in self.__data.get("worker", {}).items():
            if worker_data.get("rent_remain", 999999) <= 0:
                rent_worker.append(int(worker_slot))
        available_worker = [x for x in available_worker if x not in rent_worker]
        print('➡ src/mine/Mine.py:47 available_workers:', available_worker)
        return available_worker

    def __get_worker_busy(self, worker_slot) -> int:
        worker_status = int(self.__data.get("worker", {}).get(str(worker_slot), {}).get("productionid", 999)) # not 0 = harvestable or while harvesting, 0 = idle
        print('➡ src/biogas/Biogas.py:323 var:', worker_status)
        return worker_status

    def __get_free_production_area_slots(self, production_area) -> list:
        free_slots = ['1','2']
        if self.__data.get("productions", 0):
            used_slots = list(self.__data.get("productions", {}).get(production_area, {}).keys())
            print('➡ src/biogas/Biogas.py:341 used_slots:', used_slots)
            free_slots = [x for x in free_slots if x not in used_slots]
        print('➡ src/biogas/Biogas.py:342 free_slots:', free_slots)
        return free_slots

    def __select_items(self, item_name, count = 1) -> list:
        print('➡ src/biogas/Biogas.py:340 item_name:', item_name)
        items_id = []

        for item_id, item_data in self.__data.get("items", {}).items():
            if not item_data.get("instock", "0") == "1":
                continue
            if item_data.get("name", "") == item_name:
                items_id.append(item_id)
        if len(items_id) < count:
            for i in range (count - len(items_id)):
                content = self.__http.buy_item(item_name)
                self.__set_data(content)
                items_id.append(list(self.__data.get("items", {}).keys())[-1])
        print('➡ src/mine/Mine.py:206 axe_id:', items_id)
        print('➡ src/mine/Mine.py:206 axe_id:', len(items_id))
        if len(items_id) < count: return []

        return items_id
