#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.note.Http import Http

class Note():
    """This class handles reading from the user notes"""
    #BG- Тази класа данни съдържа цялата важна информация за бележката.

    # TODO Add fn to write into notes
  
    def __init__(self):
        self._httpConn = Http()

    def getNote(self):
      return self._httpConn.getNote()

    def getMinStock(self, plantName = None) -> int:
      note = self.getNote()
      note = note.replace('\r\n', '\n')
      lines = note.split('\n')

      isPlantGiven = not plantName is None
      for line in lines:
        if line.strip() == '':
          continue

        if not isPlantGiven and line.startswith('minStock:'):
          return self.__extractAmount(line, 'minStock:')

        if isPlantGiven and line.startswith(f'minStock({plantName}):'):
          return self.__extractAmount(line, f'minStock({plantName}):')

      # Return default 0 if not found in note
      #BG- Връща задание 0 ако не е намерена в бележката
      return 0

    def __extractAmount(self, line, prefix) -> int:
      minStockStr = line.replace(prefix, '').strip()
      minStockInt = 0
      try:
        minStockInt = int(minStockStr)
      except:
        print(f'Error: "{prefix}" must be an int')
      return minStockInt
