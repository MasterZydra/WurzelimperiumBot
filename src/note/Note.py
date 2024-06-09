#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.note.Http import Http

class Note():
    """This class handles reading from the user notes"""

    def __init__(self):
        self.__http = Http()

    def get_note(self):
        return self.__http.get_note()

    def __extract_amount(self, line, prefix) -> int:
        minStockStr = line.replace(prefix, '').strip()
        try:
            return int(minStockStr)
        except:
            print(f'Error: "{prefix}" must be an int')
        return 0

    def get_min_stock(self, plant_name = None) -> int:
        note = self.get_note().replace('\r\n', '\n')
        lines = note.split('\n')

        is_plant_given = not plant_name is None
        for line in lines:
            if line.strip() == '':
                continue

            if not is_plant_given and line.startswith('minStock:'):
                return self.__extract_amount(line, 'minStock:')

            if is_plant_given and line.startswith(f'minStock({plant_name}):'):
                return self.__extract_amount(line, f'minStock({plant_name}):')

        # Return default 0 if not found in note
        return 0

    def get_grow_only(self) -> list[str]:
        note = self.get_note().replace('\r\n', '\n')
        lines = note.split('\n')

        for line in lines:
            if line.strip() == '' or not line.startswith('growOnly:'):
                continue

            line = line.replace('growOnly:', '').strip()
            return list(map(str.strip, line.split(',')))

        # Return default [] if not found in note
        return []