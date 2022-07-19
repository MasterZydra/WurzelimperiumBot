#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Note():
    """
    Diese Daten-Klasse enthält alle wichtigen Informationen über die Notiz.
    """

    def __init__(self, httpConnection):
        self._httpConn = httpConnection

    def getNote(self):
      return self._httpConn.getNote()

    def getMinStock(self):
      note = self.getNote()
      note = note.replace('\r\n', '\n')
      lines = note.split('\n')
      for line in lines:
        if line.strip() == '':
          continue

        if line.startswith('minStock:'):
          minStockStr = line.replace('minStock:', '').strip()
          minStockInt = 0
          try:
            minStockInt = int(minStockStr)
          except:
            print('Error: "minStock" must be an int')
          return minStockInt
      # Return default 0 if not found in note
      return 0