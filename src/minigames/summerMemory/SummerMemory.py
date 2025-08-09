#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import time
from src.logger.Logger import Logger
from src.minigames.summerMemory.Http import Http

class SummerMemory:
    def __init__(self):
        self.__http = Http()

    def is_available(self, page_content: str) -> bool:
        if 'id="memory" class="summer"' not in page_content:
            return False

        # Check for rounds
        content = self.__http.init_game()
        if content is None:
            return False
        return 'round' in content['data']['data'] and content['data']['data']['round'] != 11

    def play(self) -> bool:
        if not self.flip_cards():
            return False

        return self.exchange()

    def flip_cards(self) -> bool:
        positions = list(range(1, 21))
        random.shuffle(positions)

        # { card_type -> [positions] }
        flipped_types = {}

        game_data = self.__http.init_game()
        if game_data is None:
            return False

        round = game_data['data']['data']['round']
        while round != 11:
            # Check for a known pair
            pair = None
            for card_type, pos_list in flipped_types.items():
                if len(pos_list) == 2:
                    pair = pos_list
                    del flipped_types[card_type]
                    break

            # Flip known pair
            if pair:
                pos1, pos2 = pair
                if self.__http.flip(pos1) is None:
                    return False
                time.sleep(random.choice([0, 3]))
                if self.__http.flip(pos2) is None:
                    return False
                time.sleep(random.choice([0, 3]))
                round += 1
                continue

            # Flip random unmatched card
            content = self.__http.flip(positions.pop(0))
            if content is None:
                return False
            # TODO Remove after bug is found: From time to time this section breaks
            if not isinstance(content['data'], dict):
                Logger().info('SummerMemory.flip_cards: ' + str(content))
                return False
            if content is None or 'flipped' not in content['data']:
                return False
            time.sleep(random.choice([0, 3]))

            # Search flipped cards for matching card
            next_pos = None
            for card in content['data']['flipped']:
                if 'new' in content['data']['flipped'][card]:
                    card_type = content['data']['flipped'][card]['card']
                    if card_type in flipped_types:
                        next_pos = flipped_types[card_type][0]
                        del flipped_types[card_type]
                    else:
                        flipped_types[card_type] = [card]

            # Flip second known card
            if next_pos is not None:
                content = self.__http.flip(next_pos)
                if content is None:
                    return False
                time.sleep(random.choice([0, 3]))
                round += 1
                continue

            # Flip a second random card
            content = self.__http.flip(positions.pop(0))
            if content is None or 'flipped' not in content['data']:
                return False
            time.sleep(random.choice([0, 3]))

            # Add flipped card to flipped card list
            for card in content['data']['flipped']:
                if 'new' in content['data']['flipped'][card]:
                    card_type = content['data']['flipped'][card]['card']
                    if card_type not in flipped_types:
                        flipped_types[card_type] = []
                    flipped_types[card_type].append(card)

            round += 1
            continue

        return True

    def exchange(self) -> bool:
        game_data = self.__http.init_game()
        if game_data is None:
            return False

        # Exchange all points againts plants
        points = game_data['data']['data']['points']
        while points >= 56:
            content = self.__http.exchange()
            if content is None:
                return False
            time.sleep(random.choice([0, 3]))
            points = content['data']['data']['points']

        return True
