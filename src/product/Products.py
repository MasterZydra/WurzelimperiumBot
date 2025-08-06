#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Special products
CASH = -99 # DE: Wurzeltaler

COINS = 0
CHERRY = 1 # DE: Kirsche
SALAD = 2  # DE: Salat
STRAWBERRY = 3 # DE: Erdbeere
APPLE = 4 # DE: Apfel
TOMATO = 5 # DE: Tomate
CARROT = 6 # DE: Karotte
EGGPLANT = 7 # DE: Aubergine
BLACKBERRY = 8 # DE: Brombeere
ONION = 9 # DE: Zwiebel

RASPBERRY = 10 # DE: Himbeere
CURRANT = 11 # DE: Johannisbeere
CUCUMBER = 12 # DE: Gurke
PLUM = 13 # DE: Pflaume
RADISH = 14 # DE: Radieschen
SWEET_BELL_PEPPER = 15 # DE: Paprika
COURGETTE = 16 # DE: Zucchini
MIRABELLE_PLUM = 17 # DE: Mirabelle
PUMPKIN = 18 # DE: Kürbis
WALNUT = 19 # DE: Walnuss

ASPARAGUS = 20 # DE: Spargel
PEAR = 21 # DE: Birne
POTATO = 22 # DE: Kartoffel
WELL_1 = 23 # DE: Brunnen 1
FOUNTAIN_2 = 24 # DE: Brunnen 2
DECORATIVE_STONES = 25 # DE: Dekosteine
SIDEWALK_1 = 26 # DE: Gehweg 1
SIDEWALK_2 = 27 # DE: Gehweg 2
SIDEWALK_3 = 28 # DE: Gehweg 3
PAVILION_1 = 29

PAVILION_2 = 30
PAVILION_3 = 31
CAULIFLOWER = 32 # DE: Blumenkohl
BROCCOLI = 33 # DE: Brokkoli
BLUEBERRY = 34 # DE: Heidelbeere
GARLIC = 35 # DE: Knoblauch
SPINACH = 36 # DE: Spinat
SITTING_AREA = 37 # DE: Sitzecke
ZEN_GARDEN = 38 # DE: Zengarten
POND = 39 # DE: Teich

STONE_CIRCLE = 40 # DE: Steinkreis
WEEDS = 41 # DE: Unkraut
TREE_STUMP = 42 # DE: Baumstumpf
STONE = 43 # DE: Stein
GARDEN_GNOME = 44 # DE: Gartenzwerge
MOLE = 45 # DE: Maulwurf
SIDEWALK_4 = 46 # DE: Gehweg 4
WOODEN_BALLS = 47 # DE: Holzkugeln
SUNFLOWER = 48 # DE: Sonnenblume
MARIGOLD = 49 # DE: Ringelblume

ROSE = 50 # DE: Rose
LILY = 51 # DE: Lilie
CORNFLOWER = 52 # DE: Kornblume
ORCHID = 53 # DE: Orchidee
CROCUS = 54 # DE: Krokus
OLIVE = 55
FIREPLACE = 56 # DE: Feuerstelle
SCARECROW = 57 # DE: Vogelscheuche
GERBERA = 58
LAVENDER = 59 # DE: Lavendel

TULIP = 60 # DE: Tulpe
RED_CABBAGE = 61 # DE: Rotkohl
SANDPIT = 62 # DE: Sandkasten
SLIDE = 63 # DE: Rutsche
COFFEE = 64 # DE: Kaffee
COCONUT = 65 # DE: Kokosnuss
PALM_TREE = 66 # DE: Palme
GRAPE = 67 # DE: Traube
LEMON = 68 # DE: Zitrone
MUSHROOM = 69 # DE: Champignon

BASIL = 70 # DE: Basilikum
ORANGE = 71 # DE: Orange
COCOA = 72 # DE: Kakao

BEAN = 181 # DE: Bohne

FIELD_MINT = 225 # DE: Ackerminze

PORCINI = 268 # DE: Steinpilz
CHANTERELLE = 269 # DE: Pfifferlig
MOREL = 270 # DE: Speisemorchel
OYSTER_MUSHROOM = 271 # DE: Kräuter_Seitling
GIANT_PUFFBALL = 272 # DE: Riesenträuchling

# Booster
EAGER_UNICORN_EBERHARD = 273 # DE: Eifriges Einhorn Eberhard
DROLLY_DRAGON_DIETMAR = 274 # DE: Drolliger Drache Dietmar
YODELING_YETI_JURGEN = 282 # DE: Jodelnder Yeti Jürgen
PUGGY_MERMAID_MECHTHILD = 324 # DE: Mopsige Meerjungfrau Mechthild
PITCH_WET_PENGUIN_PINGPIN = 330 # DE: Pitschnasser Pinguin Pingpin
TOOTLE_DWARF = 333 # DE: Trötenzwerg
WILD_WORLD_CHAMPION_WOLF_WILLIBALL = 344 # DE: Wilder Weltmeister-Wolf Williball
CRUSTY_CRAB_KARL = 345 # DE: Krosse Krabbe Karl
SNOW_BLIND_SNOW_HARE_SCHORSCH = 363 # DE: Schneeblinder Schneehase Schorsch
FLUFFY_PINATA_PAUL = 366 # DE: Puschelige Pinata Paul
COZY_LUCKY_CAT_GISELA = 370 # DE: Gemütliche Glückskatze Gisela
STALK_EYED_STARFISH_SOREN = 372 # DE: Stieläugiger Seestern Sören
ICY_POLAR_BEAR_EDGAR = 435 # DE: Eisiger Eisbär Edgar
CHUBBY_MOLE_MANFRED = 436 # DE: Molliger Maulwurf Manfred
PINK_BALLOON_POODLE_PUPSI = 438 # DE: Pinker Ballon-Pudel Pupsi
GRUMPY_CLAM_MICHAEL = 446 # DE: Mürrische Muschel Michael
RUDI_THE_ROARING_REINDEER = 455 # DE: Röhrendes Rentier Rudi
CHEERFUL_OTTER_FERDINAND = 456 # DE: Fideler Fischotter Ferdinand
LUCKY_GOLDEN_CAT_GARRY = 476 # DE: Goldene Glückskatze Garry
STRICT_REFEREE_SOREN = 480 # DE: Strenger Schiedsrichter Sören
OCTOPUS_KIRIL = 481 # DE: Krakelige Krake Kiril
NARROW_MOUTHED_OWL_EUSEBIUS = 488 # DE: Engstirnige Eule Eusebius
SHY_PORPOISE_SHELLY = 490 # DE: Schüchterner Schweinswal Schelly
CONFETTI_RABBIT_KUNIBERT = 493 # DE: Konfetti-Kaninchen Kunibert
LUCKY_DIAMOND_CAT = 498 # DE: Diamantene Glückskatze
ANGRY_WALRUS_WALTER = 500 # DE: Wütendes Walross Walter
ARCTIC_WOLF_BRUCE_SCHNEE = 506 # DE: Polarwolf Bruce Schnee
VORACIOUS_GARDEN_DORMOUSE_GERALT = 508 # DE: Gefräßiger Gartenschläfer Geralt
CHEERFUL_PARTY_GNOME_FERDINAND = 510 # DE: Fröhlicher Feierzwerg Ferdinand
LUCKY_CAT_MADE_OF_JADE = 515 # DE: Glückskatze aus Jade
SWIMMING_SEAHORSE_SIGGI = 517 # DE: Schwimmendes Seepferdchen Siggi
STRONG_SNOW_BUNNY_SASCHA = 522 # DE: Starker Schneehase Sascha
IMAGINATIVE_HEDGEHOG_IRWIN = 523 # DE: Ideenreicher Igel Irwin
TEA_CUP_TRIP = 525 # DE: Teetassenfahrt
DANDELION = 531 # DE: Pustezwerg
NICE_HIPPO_NILSBERT = 533 # DE: Nettes Nilpferd Nilsbert
GIFTED_BALL_ARTIST_BERND = 535 # DE: Begabter Ballkünstler Bernd
SOPHISTICATED_SEAL = 538 # DE: Raffinierte Robbengang
ALPINE_SNOW_RABBIT_ALBERT = 540 # DE: Alpiner Alpenschneehase Albert
ORGAN_PLAYER_OLAF = 542 # DE: Orgelspieler Olaf
ZEN_GARDEN_MASTER = 547 # DE: Zengarten-Meister
SERIOUS_SARDINE_SALLY = 548 # DE: Seriöse Sardine Sally
BALL_ASSISTANTS_BORIS_AND_BERT = 551 # DE: Ballassistenten Boris und Bert

def is_booster(id: int) -> bool:
    return id in {
        EAGER_UNICORN_EBERHARD, DROLLY_DRAGON_DIETMAR, YODELING_YETI_JURGEN, PUGGY_MERMAID_MECHTHILD,
        PITCH_WET_PENGUIN_PINGPIN, TOOTLE_DWARF, WILD_WORLD_CHAMPION_WOLF_WILLIBALL, CRUSTY_CRAB_KARL,
        SNOW_BLIND_SNOW_HARE_SCHORSCH, FLUFFY_PINATA_PAUL, COZY_LUCKY_CAT_GISELA, STALK_EYED_STARFISH_SOREN,
        ICY_POLAR_BEAR_EDGAR, CHUBBY_MOLE_MANFRED, PINK_BALLOON_POODLE_PUPSI, GRUMPY_CLAM_MICHAEL,
        RUDI_THE_ROARING_REINDEER, CHEERFUL_OTTER_FERDINAND, LUCKY_GOLDEN_CAT_GARRY, STRICT_REFEREE_SOREN,
        OCTOPUS_KIRIL, NARROW_MOUTHED_OWL_EUSEBIUS, SHY_PORPOISE_SHELLY, CONFETTI_RABBIT_KUNIBERT,
        LUCKY_DIAMOND_CAT, ANGRY_WALRUS_WALTER, ARCTIC_WOLF_BRUCE_SCHNEE, VORACIOUS_GARDEN_DORMOUSE_GERALT,
        CHEERFUL_PARTY_GNOME_FERDINAND, LUCKY_CAT_MADE_OF_JADE, SWIMMING_SEAHORSE_SIGGI, STRONG_SNOW_BUNNY_SASCHA,
        IMAGINATIVE_HEDGEHOG_IRWIN, TEA_CUP_TRIP, DANDELION, NICE_HIPPO_NILSBERT,
        GIFTED_BALL_ARTIST_BERND, SOPHISTICATED_SEAL, ALPINE_SNOW_RABBIT_ALBERT, ORGAN_PLAYER_OLAF,
        ZEN_GARDEN_MASTER, SERIOUS_SARDINE_SALLY, BALL_ASSISTANTS_BORIS_AND_BERT,
    }
