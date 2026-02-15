#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.birds.Http import Http
from src.logger.Logger import Logger
from src.product.Product import Product
from src.product.ProductData import ProductData
from src.shop.Shop import Shop
from src.stock.Stock import Stock
import math

class Birds:
    def __init__(self):
        self.__http = Http()
        self.__shop = Shop()
        self.__stock = Stock()
        self.__data = None
        self.update()

    def update(self):
        self.__set_data(self.__http.get_info())

    def __set_data(self, content):
        self.__data = content.get("data", None)
        self.__houses = self.__data["data"]["houses"]
        self.__jobs = self.__data["data"]["jobs"]
        self.__contest = self.__data["contest"]

    def __get_house_bird_endurance(self, house):
        return self.__houses.get(house, {}).get("bird", {}).get("endurance", 0)
    
    def __get_house_bird_load_max(self, house):
        return self.__houses.get(house, {}).get("bird", {}).get("load_max", 0)

    def __get_available_houses(self) -> list:
        return list(self.__houses.keys())

    def __get_occupied_houses(self) -> list:
        occupied_houses = []
        for job_id, job_data in self.__jobs.items():
            house = job_data.get("house", None)
            if not job_data.get("house", None) == "0":
                occupied_houses.append(house)
        return occupied_houses
    
    def __get_free_jobs(self) -> list:
        free_jobs = []
        for job_id, job_data in self.__jobs.items():
            if job_data.get("house", None) == "0" and job_data.get("remove_remain", 0) <= 0:
                free_jobs.append(job_id)
        Logger().print(f'➡ src/birds/Birds.py:55 free_jobs: {free_jobs}')
        return free_jobs

    # Job nicht zugeteilt
    """
    id	"692158"
    unr	"1458480"
    slot	"5"
    size	"1"
    distance	"3"
    endurance	"3"
    products	{ 2: 2286, 59: 1 }
    rewards	{ money: 1362, points: 1010, feather: 23, … }
    house	"0"
    duration	"0"
    remove_cooldown	"0"
    createdate	"1755676482"
    startdate	"0"
    finishdate	"0"
    """

    # Job fertig
    """
    id	"649411"
    unr	"1458480"
    slot	"2"
    size	"2"
    distance	"2"
    endurance	"3"
    products	{ 11: 32, 409: 1, 410: 3 }
    rewards	{ money: 1356, points: 520, feather: 13, … }
    house	"4"
    duration	"14400"
    remove_cooldown	"0"
    createdate	"1740912679"
    startdate	"1740912752"
    finishdate	"0"
        remain	-14750096
    """

    # Job running
    """
    id	"692159"
    unr	"1458480"
    slot	"6"
    size	"2"
    distance	"3"
    endurance	"4"
    products	{ 12: 1073, 36: 77, 410: 2 }
    rewards	{ money: 2117, points: 1020, feather: 24, … }
    house	"3"
    duration	"28800"
    remove_cooldown	"0"
    createdate	"1755676602"
    startdate	"1755677541"
    finishdate	"0"
        remain	28800
    """


    def finish_jobs(self) -> None:
        for job, data in self.__jobs.items():
            remain = data.get("remain", 0)
            slot = data.get("slot", 0)
            if remain < 0 and slot:
                Logger().print(f"Finish job in slot {slot}")
                content = self.__http.finish_job(slot)
                self.__set_data(content)

    def feed_and_renew_birds(self, buy_from_shop: bool = True, bird_nr = 5) -> None:
        for house, data in self.__houses.items():
            if house in self.__get_occupied_houses():
                continue

            bird = data.get("bird", 0)
            if bird:
                # If a bird is in the house, check if feeding is necessary
                feed_products = bird.get("feed", {})
                endurance = bird.get("endurance", 0)
                endurance_max = bird.get("endurance_max", 0)
                if endurance < endurance_max and self.__check_feed_products(feed_products, buy_from_shop):
                    Logger().print(f"Feeding bird in house {house}")
                    content = self.__http.feed_bird(house)
                    self.__set_data(content)
            else:
                # If no bird is in the house, buy a new one
                # TODO: not tested
                Logger().print(f"Buying bird {bird_nr} for house {house}")
                content = self.__http.buy_bird(house, bird_nr)
                self.__set_data(content)

    def __check_feed_products(self, feed_products: dict, buy_from_shop: bool) -> bool:
        for pid, amount in feed_products.items():
            product: Product = ProductData().get_product_by_id(pid)
            if not product:
                Logger().print("ERROR3 - no product found")
                return False

            if self.__stock.get_stock_by_product_id(pid) < amount:
                if not buy_from_shop:
                    Logger().print("ERROR1 - buying disabled")
                    return False

                buy = self.__shop.buy(product_name=pid, amount=amount)
                if not buy:
                    return False

        return True

    def start_birds(self, buy_from_shop: bool = True):
        free_houses = [x for x in self.__get_available_houses() if x not in self.__get_occupied_houses()]
        impossible_jobs=[]

        for house in free_houses:
            possible_jobs={}
            #TODO: get best job (maximize rewards?!)
            for job in self.__get_free_jobs():
                Logger().print(f'\n➡ src/birds/Birds.py:242 impossible_jobs: {impossible_jobs}')
                Logger().print(f'➡ src/birds/Birds.py:192 job: {job}')
                job_data = self.__jobs.get(job, 0)
                if not job_data:
                    if job not in impossible_jobs:
                        impossible_jobs.append(job)
                    continue
                Logger().print(f'➡ src/birds/Birds.py:195 job_data: {job_data}')
                job_size = job_data.get("size", 0) #str; size --> load --> load_max of bird
                Logger().print(f'➡ src/birds/Birds.py:216 job_size: {job_size}')
                load = 999
                match job_size:
                    case "1":
                        load = 1
                    case "2":
                        load = 2
                    case "3":
                        load = 4
                    case "4":
                        load = 6
                    case "5":
                        load = 8
                Logger().print(f'➡ src/birds/Birds.py:234 self.__get_house_bird_load_max(): {self.__get_house_bird_load_max(house)}')
                if not self.__get_house_bird_load_max(house) >= load:
                    if job not in impossible_jobs:
                        impossible_jobs.append(job)
                    continue
                Logger().print("load ok")

                job_distance = job_data.get("distance", 0) #not relevant (je höher, desto mehr rewards)
                Logger().print(f'➡ src/birds/Birds.py:220 job_distance: {job_distance}')

                job_endurance = job_data.get("endurance", 0)#str; compare with bird_endurance
                Logger().print(f'➡ src/birds/Birds.py:222 job_endurance: {job_endurance}')
                if not self.__get_house_bird_endurance(house) >= int(job_endurance):
                    if job not in impossible_jobs:
                        impossible_jobs.append(job)
                    continue
                Logger().print("endurance ok")

                if job in impossible_jobs:
                    impossible_jobs.remove(job)

                job_products = job_data.get("products", 0)#dict; check Stock if available; if not buy
                for pid, amount in job_products.items():
                    if self.__stock.get_stock_by_product_id(pid) < amount:
                        if buy_from_shop:
                            self.__shop.buy(product_name=pid, amount=amount)
                        else:
                            return #TODO: log error

                job_rewards = job_data.get("rewards", 0)#TODO: for future, maybe calc best combination...?!
                Logger().print(f'➡ src/birds/Birds.py:238 job_rewards: {job_rewards}')

                possible_jobs.update({job: job_rewards.get("xp", 0)})
            Logger().print(f'➡ src/birds/Birds.py:264 possible_jobs: {possible_jobs}')
            if possible_jobs:
                best_job = max(possible_jobs, key=possible_jobs.get)
            else:
                Logger().print(f'No job for house {house} available')
                continue
            Logger().print(f'Starting job for house {house}')
            content = self.__http.start_job(jobslot=best_job, house_nr=house)
            self.__set_data(content)

        for job in impossible_jobs:
            Logger().print(f'Removing impossible job {job}')
            content = self.__http.remove_job(slot=job)
            self.__set_data(content)

    def check_contest(self, buy_from_shop = True):
        if self.__data["data"]["level"] < 3:
            return

        # check if contest available
        if '10' in self.__jobs.keys():
            Logger().debug(f'➡ src/birds/Birds.py:246 self.__jobs: {self.__jobs}')
            Logger().info("### CONTEST STILL ACTIVE ###")
            return False
        
        # select free house/bird #TODO: endurance >= 3
        free_houses = [x for x in self.__get_available_houses() if x not in self.__get_occupied_houses()]
        Logger().debug(f'➡ src/birds/Birds.py:195 free_houses: {free_houses}')
        house = free_houses[0]
        Logger().debug(f'➡ src/birds/Birds.py:250 house: {house}')
        if not house: return False

        # select (boosted) products and start bird/contest
        boosted_products = self.__contest.get("booster", None) #list
        last_entry = self.__contest.get("entry", {}).get("products", {})# dict with pid: amount
        last_entry = {int(k):int(v) for k,v in last_entry.items()} #convert str to int
        last_entry_products = list(last_entry.keys()) #convert dict to list
        Logger().debug(f'➡ src/birds/Birds.py:269 last_entry_products: {last_entry_products}')
        boosted_products_available = [x for x in boosted_products if x not in last_entry]
        Logger().debug(f'➡ src/birds/Birds.py:273 boosted_products_available: {boosted_products_available}')

        products = {"1":{},"2":{},"3":{}}#{"1":{"pid":17,"amount":5},"2":{"pid":32,"amount":71},"3":{"pid":35,"amount":53}}
        job_products = boosted_products_available[:3] #select first 3 boosted products
        Logger().debug(f'➡ src/birds/Birds.py:276 job_products: {job_products}')
        counter=1
        load_max = self.__get_house_bird_load_max(house)*200
        Logger().debug(f'➡ src/birds/Birds.py:285 load_max: {load_max}')

        for pid in job_products:
            product: Product = ProductData().get_product_by_id(pid)
            price = product.get_price_npc()
            amount = math.ceil(load_max/3/price)
            if self.__stock.get_stock_by_product_id(pid) < amount:
                if buy_from_shop:
                    self.__shop.buy(product_name=pid, amount=amount)
                else:
                    Logger().error("### BUYING IN SHOP DISABLED")
                    return False
            products.update({f"{counter}": {"pid": pid, "amount": amount}})
            Logger().debug(f'➡ src/birds/Birds.py:290 products: {products}')
            counter=counter+1
        Logger().info("\n\n\n ### START CONTEST ###")
        content = self.__http.start_contest(house, products)
        self.__set_data(content)