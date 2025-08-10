#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Bonsais
MAIDENHAIR_PINE = 1 # DE: Mädchenkiefer
MANGROVE = 2
MONEY_TREE = 3 # DE: Geldbaum
SPRUCE_FOREST = 4 # DE: Fichten-Wald
CYPRESS = 5 # DE: Zypresse
JUNIPER = 6 # DE: Wacholder
OAK = 7 # DE: Eiche
MAPLE = 8 # DE: Ahorn
ASH = 9 # DE: Esche
CHERRY_TREE = 10 # DE: Kirschbaum

TREE_LEVELS = [
    (3, MANGROVE),
    (5, MONEY_TREE),
    (7, SPRUCE_FOREST),
    (9, CYPRESS),
    (11, JUNIPER),
    (13, OAK),
    (15, MAPLE),
    (17, ASH),
    (19, CHERRY_TREE)
]

# Pots
SIMPLE_POT = 11 # DE: Einfache Schale
GOLDEN_POT = 12 # DE: Goldene Schale
SQUARE_POT = 13 # DE: Eckiger Topf
ORGANIC_POT = 14 # DE: Organische Schale
PAINTED_POT = 15 # DE: Bemalter Topf
SQUARE_POT_WITH_FLOWERS = 16 # DE: Eckige Schale mit Blüten
BLUE_POT = 17 # DE: Blauer Topf
GLASS_POT = 18 # DE: Glasschale
ANTIQUE_POT = 19 # DE: Antike Schale
DECORATED_POT  = 20 # DE: Verzierte Schale

# Scissors
NORMAL_SCISSOR = 21 # DE: Normale Schere
POINTS_BOOSTER_SCISSOR = 22 # DE: Punkte-Booster-Schere
BONSAI_BOOSTER_SCISSOR = 23 # DE: Bonsai-Booster-Schere
SUPER_SCISSOR = 24 # DE: Super-Schere

# Pack id, charges, price
SCISSOR_PACKS = [
    (1, 10, 2000),
    (2, 240, 9000),
    (3, 100, 17000),
    (4, 500, 80000)
]

def get_tree_price(tree: int) -> list|None:
    if tree == MAIDENHAIR_PINE:
        return [5000, 'money']
    if tree == MANGROVE:
        return [1000, 'money']
    if tree == MONEY_TREE:
        return [20, 'coins']
    return None