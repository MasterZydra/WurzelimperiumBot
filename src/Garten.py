#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

class Garden():
    
    _lenX = 17
    _lenY = 12
    _nMaxFields = _lenX * _lenY
    
    def __init__(self, httpConnection, gardenID):
        self._httpConn = httpConnection
        self._id = gardenID
        self._logGarden = logging.getLogger('bot.Garden_' + str(gardenID))
        self._logGarden.setLevel(logging.DEBUG)

    def _getAllFieldIDsFromFieldIDAndSizeAsString(self, fieldID, sx, sy):
        """
        Rechnet anhand der fieldID und Größe der Pflanze (sx, sy) alle IDs aus und gibt diese als String zurück.
        """
        
        # Zurückgegebene Felderindizes (x) für Pflanzen der Größe 1-, 2- und 4-Felder.
        # Wichtig beim Gießen; dort müssen alle Indizes angegeben werden.
        # (Sowohl die mit x als auch die mit o gekennzeichneten).
        # x: fieldID
        # o: ergänzte Felder anhand der size
        # +---+   +---+---+   +---+---+
        # | x |   | x | o |   | x | o |
        # +---+   +---+---+   +---+---+
        #                     | o | o |
        #                     +---+---+
        
        if (sx == 1 and sy == 1): return str(fieldID)
        if (sx == 2 and sy == 1): return str(fieldID) + ',' + str(fieldID + 1)
        if (sx == 1 and sy == 2): return str(fieldID) + ',' + str(fieldID + 17)
        if (sx == 2 and sy == 2): return str(fieldID) + ',' + str(fieldID + 1) + ',' + str(fieldID + 17) + ',' + str(fieldID + 18)
        self._logGarden.debug('Error der plantSize --> sx: ' + str(sx) + ' sy: ' + str(sy))

    def _getAllFieldIDsFromFieldIDAndSizeAsIntList(self, fieldID, sx, sy):
        """
        Rechnet anhand der fieldID und Größe der Pflanze (sx, sy) alle IDs aus und gibt diese als Integer-Liste zurück.
        """
        sFields = self._getAllFieldIDsFromFieldIDAndSizeAsString(fieldID, sx, sy)
        listFields = sFields.split(',') #Stringarray
                        
        for i in range(0, len(listFields)):
            listFields[i] = int(listFields[i])
            
        return listFields
    
    def _isPlantGrowableOnField(self, fieldID, emptyFields, fieldsToPlant, sx):
        """
        Prüft anhand mehrerer Kriterien, ob ein Anpflanzen möglich ist.
        """
        # Betrachtetes Feld darf nicht besetzt sein
        if not (fieldID in emptyFields): return False
        
        # Anpflanzen darf nicht außerhalb des Gartens erfolgen
        # Dabei reicht die Betrachtung in x-Richtung, da hier ein
        # "Zeilenumbruch" stattfindet. Die y-Richtung ist durch die
        # Abfrage abgedeckt, ob alle benötigten Felder frei sind.
        # Felder außerhalb (in y-Richtung) des Gartens sind nicht leer,
        # da sie nicht existieren.
        if not ((self._nMaxFields - fieldID)%self._lenX >= sx - 1): return False
        fieldsToPlantSet = set(fieldsToPlant)
        emptyFieldsSet = set(emptyFields)
        
        # Alle benötigten Felder der Pflanze müssen leer sein
        if not (fieldsToPlantSet.issubset(emptyFieldsSet)): return False
        return True

    def getID(self):
        """
        Gibt die Garten ID aus dem Spiel zurück.
        """
        return self.__id

    def waterPlants(self):
        """
        Ein Garten mit der gardenID wird komplett bewässert.
        """
        self._logGarden.info('Gieße alle Pflanzen im Garten ' + str(self._id) + '.')
        try:
            plants = self._httpConn.getPlantsToWaterInGarden(self._id)
            nPlants = len(plants['fieldID'])
            for i in range(0, nPlants):
                sFields = self._getAllFieldIDsFromFieldIDAndSizeAsString(plants['fieldID'][i], plants['sx'][i], plants['sy'][i])
                self._httpConn.waterPlantInGarden(self._id, plants['fieldID'][i], sFields)
        except:
            self._logGarden.error('Garten ' + str(self._id) + ' konnte nicht bewässert werden.')
        else:
            self._logGarden.info('Im Garten ' + str(self._id) + ' wurden ' + str(nPlants) + ' Pflanzen gegossen.')
            print('Im Garten ' + str(self._id) + ' wurden ' + str(nPlants) + ' Pflanzen gegossen.')

    def getEmptyFields(self):
        """
        Gibt alle leeren Felder des Gartens zurück.
        """
        try:
            tmpEmptyFields = self._httpConn.getEmptyFieldsOfGarden(self._id)
        except:
            self._logGarden.error('Konnte leere Felder von Garten ' + str(self._id) + ' nicht ermitteln.')
        else:
            return tmpEmptyFields

    def getWeedFields(self):
        """
        Gibt alle Unkraut-Felder des Gartens zurück.
        """
        try:
            tmpWeedFields = self._httpConn.getWeedFieldsOfGarden(self._id)
        except:
            self._logGarden.error('Konnte leere Felder von Garten ' + str(self._id) + ' nicht ermitteln.')
        else:
            return tmpWeedFields

    def harvest(self):
        """
        Erntet alles im Garten.
        """
        try:
            self._httpConn.harvestGarden(self._id)
        except:
            raise
        else:
            pass

    def growPlant(self, plantID, sx, sy, amount):
        """
        Pflanzt eine Pflanze beliebiger Größe an.
        """
        
        planted = 0
        emptyFields = self.getEmptyFields()
        
        try:
            for field in range(1, self._nMaxFields + 1):
                if planted == amount: break

                fieldsToPlant = self._getAllFieldIDsFromFieldIDAndSizeAsIntList(field, sx, sy)
                
                if (self._isPlantGrowableOnField(field, emptyFields, fieldsToPlant, sx)):
                    fields = self._getAllFieldIDsFromFieldIDAndSizeAsString(field, sx, sy)
                    self._httpConn.growPlant(field, plantID, self._id, fields)
                    planted += 1

                    #Nach dem Anbau belegte Felder aus der Liste der leeren Felder loeschen
                    fieldsToPlantSet = set(fieldsToPlant)
                    emptyFieldsSet = set(emptyFields)
                    tmpSet = emptyFieldsSet - fieldsToPlantSet
                    emptyFields = list(tmpSet)

        except:
            self._logGarden.error('Im Garten ' + str(self._id) + ' konnte nicht gepflanzt werden.')
            return 0
        else:
            msg = 'Im Garten ' + str(self._id) + ' wurden ' + str(planted) + ' Pflanzen gepflanzt.'
            self._logGarden.info(msg)
            print(msg)
            return planted


class AquaGarden(Garden):
    
    def __init__(self, httpConnection):
        Garden.__init__(self, httpConnection, 101)


    def waterPlants(self):
        """
        Alle Pflanzen im Wassergarten werden bewässert.
        """
        try:
            plants = self._httpConn.getPlantsToWaterInAquaGarden()
            nPlants = len(plants['fieldID'])
            for i in range(0, nPlants):
                sFields = self._getAllFieldIDsFromFieldIDAndSizeAsString(plants['fieldID'][i], plants['sx'][i], plants['sy'][i])
                self._httpConn.waterPlantInAquaGarden(plants['fieldID'][i], sFields)
        except:
            self._logGarden.error('Wassergarten konnte nicht bewässert werden.')
        else:
            self._logGarden.info('Im Wassergarten wurden ' + str(nPlants) + ' Pflanzen gegossen.')
        
    def harvest(self):
        """
        Erntet alles im Wassergarten.
        """
        try:
            self._httpConn.harvestAquaGarden()
        except:
            raise
        else:
            pass
