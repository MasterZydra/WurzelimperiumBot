#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.User import User
from src.logger.Logger import Logger
from src.shop.Shop import Shop
from src.snailracing.Http import Http
from src.snailracing.Snail import Snail
from src.stock.Stock import Stock

RACE_DURATION = 172800 #seconds; 48h
RACE_TERRAIN_ADVANTAGE = 0.2
RACE_TERRAIN_DISADVANTAGE = 0.2
RACE_EQUIPMENT = 0.1

SADDLE_1 = ["grass", "dirt"]
SADDLE_3 = ["gravel", "asphalt"]
BRIDLE_1 = ["sand", "forest"]
BRIDLE_3 = ["dirt", "mud"]

JOCKEY1 = "jockey1" #wT
JOCKEY2 = "jockey2" #Coins

class Snailracing:
    """All important information for the snailracing."""

    def __init__(self, json = 0): #TEMP ,json
        if not json:
            self.__http = Http()
            self.__user = User()
            self.__shop = Shop()
            self.__stock = Stock()

        if json:
            self.__data = json["data"]
        else:
            self.__data = None #TEMP: json

        self.__productions_slots_unlocked = []
        self.__race_energy = 0 #TEMP int(self.__data["data"]["data"]["race"]["energy"])
        if not json:
            self.update()

    def update(self):
        self.__set_data(self.__http.get_snailracing_info())

    def __set_data(self, j_content):
        self.__data = j_content['data']
        self.__race_energy = int(self.__data["data"]["race"]["energy"])
        self.__race_remain = int(self.__data["data"]["race"].get("remain", 999999999))

        # BARS
        self.__productions_slots_unlocked = self.__get_production_slots_unlocked()

    def __get_production_slots_unlocked(self) -> list:
        productions_slots_unlocked = []
        slots = self.__data["data"]["productionslots"]
        productions_slots_unlocked.append("1")
        del slots["1"]
        for slot, data in slots.items():
            if not data.get("block", 0) == 1:
                productions_slots_unlocked.append(slot)

        return productions_slots_unlocked

    def __get_production_slots_free(self) -> list:
        slots_occupied = []
        slots_free = []
        productions = self.__data.get("data", 0).get("productions", 0)
        if productions:
            for slot, data in productions.items():
                slots_occupied.append(slot)
        slots_free = [x for x in self.__productions_slots_unlocked if x not in slots_occupied]

        return slots_free

    def start_bar_production(self, bar_pid=473) -> None:
        slots_free = self.__get_production_slots_free()
        for slot in slots_free:
            if self.__check_bar_products_availability(bar_pid):
                data = self.__http.start_bar_production(slot, bar_pid)
                self.__set_data(data)
                self.__stock.update()

    def __check_bar_products_availability(self, bar_pid, buy_from_shop = True):
        bar_products = self.__get_bar_products(bar_pid)
        for pid, amount in bar_products.items():
            if self.__stock.get_stock_by_product_id(pid) < amount:
                if buy_from_shop:
                    self.__shop.buy(product_name=int(pid), amount=amount)
                else:
                    return False
        return True

    def __get_bar_products(self, bar_pid) -> dict:
        return self.__data.get("config", {}).get("products", {}).get(str(bar_pid), {}).get("products", {})

    def collect_bar_production(self) -> None:
        productions = self.__data.get("data", 0).get("productions", 0)
        if not productions: return

        for slot, data in productions.items():
            if data.get("remain", None) <= 0:
                Logger.print(f"Slot {slot} finished")
                data = self.__http.harvest_bar_production(slot)
                self.__set_data(data)

    def calculate_track_segments(self, json) -> list: #WORKS
        track_data = json["data"]["race"]["track"]
        obstacles = track_data["obstacles"]
        obstacles_px = []
        for obstacle in obstacles:
            obstacles_px.append(obstacle.get("px")) 
        del track_data["obstacles"]

        track_segments = []
        px = 0 # length of calculated segments
        px_segment = 0 # actual segment
        length_check = 0

        # segment: 1 - 100.000, 100.001 - 200.000, ...
        # obstacle: width_px = 15.000; middle_px = 7.500; length to left = 7.499; length to right = 7.500
        for segment, terrain in track_data.items():
            if segment != "30":
                next_terrain = track_data[str(int(segment)+1)]

            if any(px_segment+1 <= obstacle_px <= px_segment+107499 for obstacle_px in obstacles_px): #obstacle in segment --> segment border + 0.5*obstacle_width = x*100.000 + 7.499
                for obstacle_px in obstacles_px: # check for all obstacles
                    if px_segment+1+7499 <= obstacle_px <= px_segment+92500: #obstacle within segment borders 75000 - 92500
                        px_before_obstacle = obstacle_px - 7500
                        length_before = px_before_obstacle - px # length until start of obstacle
                        px_after_obstacle = obstacle_px + 7501
                        if length_before > 0: # segment area before obstacle starts
                            track_segments.append({"start": px+1, "end": px_before_obstacle, "length": length_before, "terrain": terrain["terrain"], "obstacle": 0})
                            length_check += length_before
                            track_segments.append({"start": px_before_obstacle+1, "end": px_after_obstacle-1, "length": 15000, "terrain": terrain["terrain"], "obstacle": 1})
                            length_check += 15000
                        else: # obstacle overlapping; length_before negative
                            track_segments.append({"start": px+1, "end": px_after_obstacle-1, "length": 15000+length_before+1, "terrain": terrain["terrain"], "obstacle": 1})
                            length_check += 15000+length_before+1
                        px += length_before + 15000

                    if px_segment + 107500 > obstacle_px > px_segment+92500: #zur nächste Segmentgrenzen
                        px_before_obstacle = obstacle_px - 7500
                        obstacle_length_before_segment_border = px_segment + 100000 - px_before_obstacle
                        length_before = px_before_obstacle - px
                        px_after_obstacle = obstacle_px + 7501
                        obstacle_length_after_segment_border = 15000 - obstacle_length_before_segment_border

                        track_segments.append({"start": px+1, "end": px_before_obstacle, "length": length_before, "terrain": terrain["terrain"], "obstacle": 0})
                        length_check += length_before
                        track_segments.append({"start": px_before_obstacle + 1, "end": px_before_obstacle + 1 + obstacle_length_before_segment_border - 1, "length": obstacle_length_before_segment_border, "terrain": terrain["terrain"], "obstacle": 1})
                        length_check += obstacle_length_before_segment_border
                        track_segments.append({"start": px_segment + 100000 + 1, "end": px_after_obstacle - 1, "length": obstacle_length_after_segment_border, "terrain": next_terrain["terrain"], "obstacle": 1})
                        length_check += obstacle_length_after_segment_border

                        px += obstacle_length_before_segment_border + length_before + obstacle_length_after_segment_border
                        length_before + 15000 + 1

                if px < px_segment + 100000: # rest of segment without obstacles
                    length = px_segment + 100000 - px
                    track_segments.append({"start": px+1, "end": px_segment+100000, "length": length, "terrain": terrain["terrain"], "obstacle": 0})
                    length_check += length
                    px += length
            else: # no obstacle within segment
                length = px_segment + 100000 - px
                track_segments.append({"start": px+1, "end": px_segment+100000, "length": length, "terrain": terrain["terrain"], "obstacle": 0})
                length_check += length
                px += length

            px_segment += 100000
        return track_segments

    def calculate_race_distance(self, track_segments, snail: Snail, saddle, bridle): # TODO:
        snail_speed = snail.get_speed()
        sliminess = snail.get_sliminess()
        race_distance = 0.0
        race_time = 0

        # EQUIPMENT
        day_night_bonus = 1.1 #1 + 0.1(helmet)
        if snail.get_daytime() == self.__data["data"]["race"]["daytime"]:
            day_night_bonus += 0.1
        else:
            day_night_bonus = day_night_bonus - 0.1

        for segment in track_segments:
            terrain = segment.get("terrain")

            terrain_speed = self.__calculate_terrain_speed(terrain, snail, saddle, bridle)

            race_speed = snail_speed * terrain_speed * day_night_bonus #m/h

            if segment.get("obstacle"):
                race_speed = race_speed * (sliminess/10)

            # ----- 20m == 100.000px
            race_time_segment = ((segment.get("length")/100000*20) / race_speed) * 3600
            if not race_time_segment <= RACE_DURATION - race_time:
                race_time_remaining = RACE_DURATION - race_time
                race_time_remaining_h = race_time_remaining/60/60

                race_distance += race_time_remaining * (race_speed / 3600)

                break

            race_time += race_time_segment

            race_time_min = race_time / 60
            race_time_h = race_time_min / 60

            race_distance += race_time_segment * (race_speed / 3600)
        return race_distance

    def __calculate_terrain_speed(self, terrain, snail: Snail, saddle, bridle):
        snail_loved = snail.get_loved()
        snail_hated = snail.get_hated()
        terrain_speed = 1
        if terrain in snail_loved:
            terrain_speed += RACE_TERRAIN_ADVANTAGE
        if terrain in snail_hated:
            terrain_speed -= RACE_TERRAIN_DISADVANTAGE
        if terrain in saddle:
            terrain_speed += RACE_EQUIPMENT
        if terrain in bridle:
            terrain_speed += RACE_EQUIPMENT

        return terrain_speed

    def calculate_optimal_snail(self):
        track_segments = self.calculate_track_segments(self.__data)

        snails = []
        for slot in range(1,5): # slots 1-4
            # if available: #snail available
            snail = Snail(self.__data, slot)
            in_race = snail.get_in_race()
            cooldown = snail.get_cooldown_remain()
            if not (int(in_race) or cooldown > 0):
                snails.append(snail)

        snails_max = []
        for slot in range(1,7): # theoretical snail 1-6 Lvl.10
            snails_max.append(Snail(self.__data, type=slot))

        snail_distance = {}
        snail: Snail
        for snail in snails:
            slot = snail.get_slot()
            temp_distance = {}
            temp_distance.update({11: self.calculate_race_distance(track_segments, snail, saddle=SADDLE_1, bridle=BRIDLE_1)})
            temp_distance.update({13: self.calculate_race_distance(track_segments, snail, saddle=SADDLE_1, bridle=BRIDLE_3)})
            temp_distance.update({31: self.calculate_race_distance(track_segments, snail, saddle=SADDLE_3, bridle=BRIDLE_1)})
            temp_distance.update({33: self.calculate_race_distance(track_segments, snail, saddle=SADDLE_3, bridle=BRIDLE_3)})

            best = [key for key in temp_distance if temp_distance[key] == max(temp_distance.values())]
            snail_distance.update({max(temp_distance.values()): {"best": best[-1], "slot": slot}})

        snail_distance_max = {}
        for snail in snails_max:
            slot = snail.get_type()
            temp_distance = {}
            temp_distance.update({11: self.calculate_race_distance(track_segments, snail, saddle=SADDLE_1, bridle=BRIDLE_1)})
            temp_distance.update({13: self.calculate_race_distance(track_segments, snail, saddle=SADDLE_1, bridle=BRIDLE_3)})
            temp_distance.update({31: self.calculate_race_distance(track_segments, snail, saddle=SADDLE_3, bridle=BRIDLE_1)})
            temp_distance.update({33: self.calculate_race_distance(track_segments, snail, saddle=SADDLE_3, bridle=BRIDLE_3)})
            best = [key for key in temp_distance if temp_distance[key] == max(temp_distance.values())]
            snail_distance_max.update({max(temp_distance.values()): {"best": best[-1], "slot": slot}})
        
        return snail_distance #list with best snail(s)

    def setup_optimal_snail(self, snail_distances: dict): #TODO: fertig, adapt for HTTP-use

        max_distance= max(snail_distances.keys())
        slot = snail_distances.get(max_distance).get("slot")

        best_items = snail_distances.get(max_distance).get("best")
        best_saddle = str(best_items)[0]
        best_headgear = str(best_items)[1]
        best_snail = Snail(self.__data, slot)
        # test if available, else remove
        #TODO:
        jockey = f"jockey{1}"

        saddle = f"saddle{best_saddle}"

        makeup = "makeup1" #Wimpel

        if self.__data["data"]["race"]["daytime"] == "day":
            helmet = f"helmet1" #day-night
        if self.__data["data"]["race"]["daytime"] == "night":
            helmet = f"helmet3"

        headgear = f"headgear{best_headgear}" #Zaumzeug

        """setup={"slot":"1","jockey":"jockey1","saddle":"saddle1","makeup":"makeup1","helmet":"helmet1","headgear":"headgear3"}"""
        setup = f'"slot":"{slot}","jockey":"{jockey}","saddle":"{saddle}","makeup":"{makeup}","helmet":"{helmet}","headgear":"{headgear}"'

        return setup

    def check_race_feeding(self, pid=473, amount=1):
        if self.__race_energy < 150000 and self.__race_remain >= 10000: 
            Logger.print("Feeding snail ...")
            content = self.__http.feed_snail(pid, amount) # feed snail with energy bar
            self.__set_data(content)

    def check_race_start(self):
        if self.__race_remain == 999999999:
            Logger.print("Staring race ...")
            dis = self.calculate_optimal_snail()
            setup = self.setup_optimal_snail(dis)
            content = self.__http.start_race(setup)
            self.__set_data(content)

    def check_race_finish(self):
        if self.__race_remain < 0:
            Logger.print("Finishing race ...")
            content = self.__http.finish_race()
            self.__set_data(content)
            reward = self.__data.get("reward", "not found")
