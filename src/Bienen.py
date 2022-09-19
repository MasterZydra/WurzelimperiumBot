#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from collections import Counter


class Honig:
    """
    Diese Daten-Klasse enthält alle wichtigen Informationen über den Honiggarten.
    """
    # Honig
    __honeyFarmAvailability = None
    __honeyFarmInfo = None
    # __hivesavailable = None
    # __honeyquestnr = None
    # __honeyquest = None

    def __init__(self, httpConnection):
        self._httpConn = httpConnection
        self._logHonig = logging.getLogger('bot.Honig')
        self._logHonig.setLevel(logging.DEBUG)

    def setHoneyFarmAvailability(self):
        self.setHoneyFarmInfo()
        self.__honeyFarmAvailability = isinstance(self.getHoneyFarmInfo()['data'], dict)
        return self.__honeyFarmAvailability

    def isHoneyFarmAvailable(self):
        return self.__honeyFarmAvailability

    def getHoneyFarmInfo(self):
        return self.__honeyFarmInfo

    def setHoneyFarmInfo(self):
        self.__honeyFarmInfo = self._httpConn.getHoneyFarmInfos()

    def getQuestHoneyNr(self):
        return self.getHoneyFarmInfo()['questnr']

    def getQuestHoney(self):
        return self.getHoneyFarmInfo()['questData']

    def getQuestHoneyProducts(self):
        products_list = self.getQuestHoney()['products']
        products = {str(product['pid']): product['missing'] for product in products_list}
        return products

    def getHoneyWimpsData(self):
        wimps_list = self.getHoneyFarmInfo()['data']['wimps']
        wimps = {}
        for wimp in wimps_list:
            wimps[wimp['id']] = [int(wimp['price']), wimp['data']]

        return wimps

    def getHoneyWimpsProducts(self):
        wimps_data = self.getHoneyWimpsData()
        products = Counter()
        for value in wimps_data.values():
            products += value[1]
        return dict(products)

    def getHivesAvailable(self):
        hives = self.getHoneyFarmInfo()['data']['data']['hives']
        available_hives = {key: value for key, value in hives.items()
                           if value.get('tour_remain', 0) <= 0
                           and not value.get('buyable', 0)}

        return available_hives

    def getHiveType(self):
        return self._httpConn.getHoneyFarmInfos()[3]

    def setHivesAvailable(self, http):
        """
        Liest die Anzahl der Hives aus und speichert ihn in der Klasse.
        """
        try:
            tmpHivesAvailable = http.getHoneyFarmInfos()[2]
        except:
            raise
        else:
            self.__hivesavailable = tmpHivesAvailable

    def setHoneyQuestNr(self, http):
        """
        Liest die Anzahl der Hives aus und speichert ihn in der Klasse.
        """
        try:
            tmpHoneyQuestnr = http.getHoneyFarmInfos()[0]
        except:
            raise
        else:
            self.__honeyquestnr = tmpHoneyQuestnr

    def setHoneyQuest(self, http):
        """
        Liest die aktuelle HoneyQuest aus und speichert ihn in der Klasse.
        """
        try:
            tmpHoneyQuest = http.getHoneyFarmInfos()[1]
        except:
            raise
        else:
            self.__honeyquest = tmpHoneyQuest

    def startAllHives(self):
        """
        Sendet alle Bienen.
        """
        available_hives = self.getHivesAvailable()
        available_products = self.getHoneyFarmInfo()['data']['garden']
        mapping = self.getHoneyFarmInfo()['data']['config']['mapping']
        if len(available_products) == 0:
            return
        for key, value in available_hives.items():
            if str(mapping.get(value.get('pid'))['pid']) in available_products.keys():
                self.startHive(key)

    def startHive(self, hive_id):
        try:
            self._httpConn.sendBienen(hive_id)
            self._logHonig.info(f'Sending Bees from hive {hive_id=}')
        except:
            raise
        else:
            self.setHoneyFarmInfo()

    # TODO: extend and create HTTP-Requests
    def changeHivesTypeQuest(self):
        """
        Ändert die Hives auf Questanfprderungen.
        """
        quest = self.__honeyquest
        for i in quest:
            if quest[i]['missing'] != 0:
                change = quest[i]['pid']
                break
            else:
                change = 315

        Questanforderung = change
        try:
            self._httpConn.changeHiveBienen(Questanforderung)
        except:
            raise
        else:
            pass
