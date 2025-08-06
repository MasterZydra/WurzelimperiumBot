#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import Enum
from src.product.Products import MUSHROOM, PORCINI, CHANTERELLE, MOREL, OYSTER_MUSHROOM, GIANT_PUFFBALL

class Care(Enum):
    WATER = "water"
    LIGHT = "light"
    FERTILIZE = "fertilize"

class Mushroom(Enum):
    MUSHROOM = MUSHROOM
    PORCINI = PORCINI
    CHANTERELLE = CHANTERELLE
    MOREL = MOREL
    OYSTER_MUSHROOM = OYSTER_MUSHROOM
    GIANT_PUFFBALL = GIANT_PUFFBALL
    GOLDEN_FLUFFBALL = 999  # DE: Goldener Flauschling

class Care_OID(Enum):
    """
    "water": [
    {
        "oid": 1,
        "level": 1,
        "points": 83,
        "duration": 28800,
        "unlock": 0
    },
    {
        "oid": 2,
        "level": 5,
        "points": 1310,
        "duration": 201600,
        "unlock": 100
    },
    {
        "oid": 3,
        "level": 9,
        "points": 187,
        "duration": 28800,
        "unlock": 160
    },
    {
        "oid": 4,
        "level": 13,
        "points": 3494,
        "duration": 201600,
        "unlock": 250
    },
    {
        "oid": 5,
        "level": 17,
        "points": 416,
        "duration": 28800,
        "unlock": 400
    },
    {
        "oid": 16,
        "level": 21,
        "points": 3640,
        "duration": 201600,
        "unlock": 1000
    }
    ]
    """
    WATER_1 = 1
    WATER_2 = 2
    WATER_3 = 3
    WATER_4 = 4
    WATER_5 = 5
    WATER_6 = 16
    """
    "light": [
    {
        "oid": 6,
        "level": 2,
        "points": 94,
        "duration": 28800,
        "unlock": 20
    },
    {
        "oid": 7,
        "level": 6,
        "points": 1310,
        "duration": 201600,
        "unlock": 120
    },
    {
        "oid": 8,
        "level": 10,
        "points": 198,
        "duration": 28800,
        "unlock": 180
    },
    {
        "oid": 9,
        "level": 14,
        "points": 3494,
        "duration": 201600,
        "unlock": 300
    },
    {
        "oid": 10,
        "level": 18,
        "points": 437,
        "duration": 28800,
        "unlock": 450
    },
    {
        "oid": 17,
        "level": 22,
        "points": 3713,
        "duration": 201600,
        "unlock": 1200
    }
    ]
    """
    LIGHT_1 = 6
    LIGHT_2 = 7
    LIGHT_3 = 8
    LIGHT_4 = 9
    LIGHT_5 = 10
    LIGHT_6 = 17
    """
    "fertilize": [
    {
        "oid": 11,
        "level": 3,
        "points": 104,
        "duration": 28800,
        "unlock": 50
    },
    {
        "oid": 12,
        "level": 7,
        "points": 1310,
        "duration": 201600,
        "unlock": 140
    },
    {
        "oid": 13,
        "level": 11,
        "points": 208,
        "duration": 28800,
        "unlock": 200
    },
    {
        "oid": 14,
        "level": 15,
        "points": 3494,
        "duration": 201600,
        "unlock": 350
    },
    {
        "oid": 15,
        "level": 19,
        "points": 458,
        "duration": 28800,
        "unlock": 500
    },
    {
        "oid": 18,
        "level": 23,
        "points": 3786,
        "duration": 201600,
        "unlock": 1500
    }
    ]
    """
    FERTILIZE_1 = 11
    FERTILIZE_2 = 12
    FERTILIZE_3 = 13
    FERTILIZE_4 = 14
    FERTILIZE_5 = 15
    FERTILIZE_6 = 18

def is_water_care_item(oid: int) -> bool:
    return oid in range(Care_OID.WATER_1.value, Care_OID.LIGHT_1.value) or oid == Care_OID.WATER_6.value

def is_light_care_item(oid: int) -> bool:
    return oid in range(Care_OID.LIGHT_1.value, Care_OID.FERTILIZE_1.value) or oid == Care_OID.LIGHT_6.value

def is_fertilize_care_item(oid: int) -> bool:
    return oid in range(Care_OID.FERTILIZE_1.value, Care_OID.WATER_6.value) or oid == Care_OID.FERTILIZE_6.value

def get_care_item_price(oid: int) -> list|None:
    match oid:
        # Water
        case Care_OID.WATER_1.value:
            return [200, 'money']
        case Care_OID.WATER_2.value:
            return [1, 'coins']
        case Care_OID.WATER_3.value:
            return [500, 'money']
        case Care_OID.WATER_4.value:
            return [2, 'coins']
        case Care_OID.WATER_5.value:
            return [30, 'fruits']
        case Care_OID.WATER_6.value:
            return [3, 'coins']

        # Light
        case Care_OID.LIGHT_1.value:
            return [200, 'money']
        case Care_OID.LIGHT_2.value:
            return [1, 'coins']
        case Care_OID.LIGHT_3.value:
            return [550, 'money']
        case Care_OID.LIGHT_4.value:
            return [2, 'coins']
        case Care_OID.LIGHT_5.value:
            return [35, 'fruits']
        case Care_OID.LIGHT_6.value:
            return [3, 'coins']

        # Fertilize
        case Care_OID.FERTILIZE_1.value:
            return [200, 'money']
        case Care_OID.FERTILIZE_2.value:
            return [1, 'coins']
        case Care_OID.FERTILIZE_3.value:
            return [600, 'money']
        case Care_OID.FERTILIZE_4.value:
            return [2, 'coins']
        case Care_OID.FERTILIZE_5.value:
            return [40, 'fruits']
        case Care_OID.FERTILIZE_6.value:
            return [3, 'coins']

    return None
