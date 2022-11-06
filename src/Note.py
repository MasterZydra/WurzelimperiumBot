#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.HTTPCommunication import HTTPConnection

class Note():
    """Diese Daten-Klasse enthält alle wichtigen Informationen über die Notiz."""

    def __init__(self, httpConnection: HTTPConnection):
        self._httpConn = httpConnection

    def getNote(self):
      return self._httpConn.getNote()

    def getMinStock(self, plantName = None):
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
      return 0

    def __extractAmount(self, line, prefix):
      minStockStr = line.replace(prefix, '').strip()
      minStockInt = 0
      try:
        minStockInt = int(minStockStr)
      except:
        print(f'Error: "{prefix}" must be an int')
      return minStockInt