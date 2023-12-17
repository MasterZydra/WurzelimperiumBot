#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from src.HTTPCommunication import HTTPConnection

class Bonsai():
    """Diese Daten-Klasse enthält alle wichtigen Informationen über den Bonsaigarten."""

    def __init__(self, httpConnection: HTTPConnection):
        self._httpConn = httpConnection
        self._logBonsai = logging.getLogger('bot.Bonsai')
        self._logBonsai.setLevel(logging.DEBUG)
        self.initialiseBonsaiInfo(self._httpConn.bonsaiInit())

    def initialiseBonsaiInfo(self, jContent):
        self.__jContentData = jContent['data'] ###TODO: only use jContent[data] --> check if is equal over all possible http requests
        self.__bonsaiquestnr = jContent['questnr']
        self.__bonsaiquest = self.__getBonsaiQuest(jContent) ###not in every jContent response
        self.__bonsaiavailable = self.__getAvailableBonsaiSlots(jContent) ###not in every jContent response
        self.__bonsaiFarmAvailability = True ###Abfrage wie die alte?
        self.__slotinfos = self.__getBonsaiSlotInfos(jContent)
    
    def setBonsaiFarmData(self, jContent):
        self.__jContentData = jContent['data']
        self.__slotinfos = self.__getBonsaiSlotInfos(jContent)

    def setBonsaiAvailability(self, bAvl): #???
        self.__bonsaiFarmAvailability = bAvl

    def isBonsaiFarmAvailable(self): #???
        return self.__bonsaiFarmAvailability

    def __getBonsaiQuest(self, jContent):
        """Sucht im JSON Content nach verfügbaren bonsaiquesten und gibt diese zurück."""
        bonsaiQuest = {}
        i = 1
        for course in jContent['questData']['products']:
            new = {i: {'pid': course['pid'], 'type': course['name']}}
            bonsaiQuest.update(new)
            i = i + 1
        return bonsaiQuest
    
    def __getAvailableBonsaiSlots(self, jContent): # noch notwendig???
        """Sucht im JSON Content nach verfügbaren bonsai und gibt diese zurück."""
        availableTreeSlots = []

        for tree in jContent['data']['data']['slots']:
            if "block" not in jContent['data']['data']['slots'][tree]:
                availableTreeSlots.append(int(tree))

        # Sortierung über ein leeres Array ändert Objekttyp zu None
        if len(availableTreeSlots) > 0:
            availableTreeSlots.sort(reverse=False)

        return availableTreeSlots
    
    def __getBonsaiSlotInfos(self, jContent):
        """Sucht im JSON Content nach den Bonsais und gibt diese zurück."""
        availableBonsais = {}

        for bonsai in jContent['data']['breed']:
            bonsaiLevel: int = jContent['data']['breed'][bonsai]['level']
            bonsaiReward: dict = jContent['data']['breed'][bonsai]['reward']
            bonsaiSlotNr = jContent['data']['breed'][bonsai]['slot']
            bonsaiBranches = jContent['data']['breed'][bonsai]['branches']
            availableBonsais[bonsaiSlotNr] = [bonsaiLevel, bonsaiReward, bonsaiBranches]

        return availableBonsais

    def cutAllBonsai(self) -> None:
        #TODO Item automatisch nach kaufen, Bonsai in den Garten setzen wenn lvl 3 erreicht
        """
        Probiert bei allen Bäumen die Äste zu schneiden
        """
        sissorID = None
        sissorLoads = 0
        for key, value in self.__jContentData['items'].items():
            if value['item'] == "21":
                sissorID = key
                sissorLoads = value['loads']
                self._logBonsai.info(f"In storage: {sissorLoads} normal scissors with ID {sissorID}")
        if sissorID is None or int(sissorLoads) < 50:
            print("No scissors found...")
            jContent = self._httpConn.buyAndPlaceBonsaiItem(21, 4, 0)
            self.setBonsaiFarmData(jContent)
        
        for key in self.__slotinfos.keys():
            self._logBonsai.info(f'Bonsai in slot {key}:')
            for branch in self.__slotinfos[key][2]:
                jContent = self._httpConn.cutBonsaiBranch(key, sissorID, branch)
                self.setBonsaiFarmData(jContent)
                self._logBonsai.info(f'Cut branch {branch}')


    def checkBonsai(self):
        """checks if bonsai is a certain level: places bonsai in bonsaigarden and renews it"""
        for key in self.__slotinfos.keys():
            level = self.__slotinfos[key][0]
            if level > 1:
                self._logBonsai.info(f'Finish Bonsai in slot {key} with level {level}')
                jContent = self._httpConn.finishBonsai(key)
                jContent = self._httpConn.buyAndPlaceBonsaiItem(11, 1, key)
                jContent = self._httpConn.buyAndPlaceBonsaiItem(5, 1, key)
                self.setBonsaiFarmData(jContent)
            else:
                self._logBonsai.info(f'Do nothing: Bonsai in slot {key} is level {level}')