class ShopProducts:
    @staticmethod
    def products() -> dict:
        return {
            "Kirsche": 1,  #BG-Череша
            "Apfel": 1,  #BG-Ябълка
            "Brombeere": 1,  #BG-Къпина
            "Himbeere": 1,  #BG-Малина
            "Johannisbeere": 1,  #BG-Касис
            "Pflaume": 1,  #BG-Слива
            "Mirabelle": 1,  #BG-Мирабела
            "Walnuss": 1,  #BG-Орех
            "Birne": 1,  #BG-Круша
            "Olive": 1,  #BG-Маслина
            "Kokosnuss": 1,  #BG-Кокос
            "Palme": 1,  #BG-Палма
            "Traube": 1,  #BG-Грозде
            "Zitrone": 1,  #BG-Лимон
            "Orange": 1,  #BG-Портокал
            "Engelstrompete": 1,  #BG-Ангелски тромпет
            "Fichtenzapfen": 1,  #BG-Шишарка
            "Fichte": 1,  #BG-Смърч
            "Salat": 2,  #BG-Маруля
            "Erdbeere": 2,  #BG-Ягода
            "Tomate": 2,  #BG-Домат
            "Karotte": 2,  #BG-Морков
            "Aubergine": 2,  #BG-Патладжан
            "Zwiebel": 2,  #BG-Лук
            "Gurke": 2,  #BG-Краставица
            "Radieschen": 2,  #BG-Репичка
            "Paprika": 2,  #BG-Чушка
            "Zucchini": 2,  #BG-Тиквичка
            "Kürbis": 2,  #BG-Тиква
            "Spargel": 2,  #BG-Аспержа
            "Kartoffel": 2,  #BG-Картоф
            "Blumenkohl": 2,  #BG-Цветно зеле
            "Brokkoli": 2,  #BG-Брокол
            "Heidelbeere": 2,  #BG-Боровинка
            "Knoblauch": 2,  #BG-Чесън
            "Spinat": 2,  #BG-Спанак
            "Rotkohl": 2,  #BG-Червено зеле
            "Kaffee": 2,  #BG-Кафе
            "Champignon": 2,  #BG-Печурка
            "Basilikum": 2,  #BG-Босилек
            "Kakao": 2,  #BG-Какао
            "Pilzgeflecht": 2,  #BG-Мрежарка
            "Fliegenpilz": 2,  #BG-Мухоморка
            "Bohne": 2,
            "Buchsbaumsetzling": 2,  #BG-Фиданка от Чемшир
            "Buchsbaum": 2,  #BG-Чемшир
            "Steinpilz": 2,  #BG-Манатарка
            "Pfifferling": 2,  #BG-Лисичка
            "Speisemorchel": 2,  #BG-Сморчок
            "Kräuter-Seitling": 2,  #BG-Стриденца
            "Riesenträuschling": 2,  #BG-Гигантски гълъб
            "Brunnen 1": 3,  #BG-Чешма 1
            "Brunnen 2": 3,  #BG-Чешма 2
            "Dekosteine": 3,  #BG-Декоративни камъни
            "Ente": 3,  #BG-Патица
            "Feuerstelle": 3,  #BG-Огнище
            "Gartenzwerge": 3,  #BG-Градински джуджета
            "Gehweg 1": 3,  #BG-Пътека 1
            "Gehweg 2": 3,  #BG-Пътека 2
            "Gehweg 3,": 3,  #BG-Пътека 3
            "Gehweg 4": 3,  #BG-Пътека 4
            "Holzkugeln": 3,  #BG-Дървени топки
            "kleines Boot": 3,  #BG-Малка лодка
            "Pavillon 1": 3,  #BG-Павилион 1
            "Pavillon 2": 3,  #BG-Павилион 2
            "Pavillon 3,": 3,  #BG-Павилион 3
            "Rutsche": 3,  #BG-Пързалка
            "Sandkasten": 3,  #BG-Пясъчник
            "Schwanenpaar": 3,  #BG-Лебедова двойка
            "Seerosenleuchte grün": 3,  #BG-Зелена лампа с водни лилии
            "Seerosenleuchte rosa": 3,  #BG-Розова лампа с водни лилии
            "Seerosenleuchte rot": 3,  #BG-Червена лампа с водни лилии
            "Seerosenleuchte türkis": 3,  #BG-Тюркоазена лампа с водни лилии
            "Sitzecke": 3,  #BG-Кът за сядане/пейка
            "Steinkreis": 3,  #BG-Кръг от камъни
            "Teich": 3,  #BG-Езеро
            "Zengarten": 3,  #BG-Японска градина
            "Sonnenblume": 4,  #BG-Слънчоглед
            "Ringelblume": 4,  #BG-Невен
            "Rose": 4,  #BG-Роза
            "Lilie": 4,  #BG-Лилия
            "Kornblume": 4,  #BG-Метличина
            "Orchidee": 4,  #BG-Орхидея
            "Krokus": 4,  #BG-Шафран
            "Gerbera": 4,  #BG-Гербер
            "Lavendel": 4,  #BG-Лавандула
            "Tulpe": 4,  #BG-Лале
            "Nickende Distel": 4,  #BG-Кимаща Трънка
            "Gemeine Wegwarte": 4,  #BG-Цикория
            "Sibirische Schwertlilie": 4,  #BG-Сибирска перуника
            "Moorlilie": 4,  #BG-Блатна лилия
            "Heidenelke": 4,
            "Leberblümchen": 4,
            "Teufelsabbiss": 4,
            "Schlüsselblume": 4,
            "Klatschmohn": 4,
            "Langblättriger Ehrenpreis": 4,
            "Besenheide": 4,
            "Großer Wiesenknopf": 4,
            "Vierblättrige Einbeere": 4,
            "Kleine Braunelle": 4,
            "Seerose": 0,  #BG-Водна лилия
            "Scheincalla": 0,  #BG-Блатна Кала
            "gelbe Teichrose": 0,  #BG-Жълта водна лилия
            "Wassersellerie": 0,  #BG-Водна Целина
            "Wasserfeder": 0,  #BG-Водна Елодея
            "Krebsschere": 0,  #BG-Воден Магарешки бодил
            "Wasserknöterich": 0,  #BG-Воден Имел
            "Rohrkolben": 0,  #BG-Папур
            "Sumpfdotterblume": 0,  #BG-Блатна Жълтурка
            "Schwertlilie": 0,  #BG-Перуника
            "Reis": 0,  #BG-Ориз
            "Schilfsetzling": 0,  #BG-Фиданка от Тръстика
            "Schilf": 0,  #BG-Тръстика
            "Schwanenblume": 0,
            "Fieberklee": 0,
        }
