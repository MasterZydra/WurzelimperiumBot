#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.core.Feature import Feature
from src.gardenhouse.Http import Http
from src.logger.Logger import Logger
from src.note.Note import Note
from datetime import datetime, timedelta
import time
import random
import re

class GardenHouse:
    def __init__(self):
        self.__http = Http()

    def collect_trophy_points(self) -> bool:
        # The time of last point collection is stored in notes
        if not Feature().is_note_available():
            return False

        if not self._is_next_day_since_last_trophy_collection():
            Logger().print("Trophy points were already collected today.")
            return False

        # Simulate the user opening the garden house
        self.__http.init()

        # Get all trophies
        data = self.__http.get_trophies()
        if data is None:
            return False

        gifts = data.get("gifts", {})
        if not isinstance(gifts, dict):
            return False

        collected_points = 0

        for gift_id, gift_data in gifts.items():
            if not isinstance(gift_data, dict) or gift_data.get("click") is not True:
                continue

            time.sleep(random.choice([0, 3]))

            data = self.__http.click_trophy(str(gift_id))
            if not isinstance(data, dict):
                continue

            msg = data.get("msg", "")
            if not isinstance(msg, str):
                continue

            match = re.search(r"(\d+)", msg)
            if not match:
                continue

            collected_points += int(match.group(1))

        Logger().print(f"Collected {collected_points} points.")

        self._write_last_trophy_collection_time()

        return True

    # Helpers

    def _write_last_trophy_collection_time(self) -> bool:
        noteText = Note().get_note()

        if Note().get_line('trophies.last_collection: ') == '':
            noteText = f"\r\ntrophies.last_collection: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        else:
            noteText = re.sub(
                r"trophies\.last_collection: .*\n",
                f"trophies.last_collection: {datetime.now().strftime('%Y-%m-%d %H:%M')}\r\n",
                noteText
            )

        return Note().write(noteText)

    def _get_last_trophy_collection_time(self) -> str:
        line = Note().get_line('trophies.last_collection: ')
        return line.replace('trophies.last_collection: ', '').strip()

    def _is_next_day_since_last_trophy_collection(self) -> bool:
        last_trophy_collection_time = self._get_last_trophy_collection_time()

        if last_trophy_collection_time == '':
            return True

        timestamp = datetime.strptime(last_trophy_collection_time, "%Y-%m-%d %H:%M")
        now = datetime.now()

        return timestamp.date() == (now.date() + timedelta(days=1))
