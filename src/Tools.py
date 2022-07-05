# -*- coding: utf-8 -*-

from prettytable import PrettyTable
from textwrap import wrap
VAL_WRAP_WIDTH = 60

def readListFromTextfile(textfile):
    """
    Liest eine Liste aus einer vorhandenen Text-Datei (.txt) ein. Dabei darf die Liste pro Zeile
    nur einen Eintrag enthalten. Die Funktion gibt die Liste als Liste (Datentyp) zurück. Tritt
    während dem Einlesen ein Fehler auf, wird eine leere Liste zurückgegeben.
    
    @param textfile: Vollständiger Pfad der zu lesenden Text-Datei
    @type textfile: String
    """

    tmpList = []
    elementsToBeDeleted = []
    
    # Inhalt der Datei als Liste einlesen
    try:
        file = open(textfile, 'r')
    except IOError:
        raise
    else:    
    
        tmpList = file.readlines()
        file.close()

        for i in range(len(tmpList)):
            # Leerzeichen entfernen
            tmpList[i] = str(tmpList[i]).strip()

            if (tmpList[i] == ''):
                elementsToBeDeleted.append(i)

        # Reihenfolge der zwischengespeicherten Indizes umkehren, um das Entfernen zu erleichtern.
        # Sonst verschieben sich die Indizes 
        elementsToBeDeleted.reverse()
        
        # Leere Eintraege entfernen
        for i in range(len(elementsToBeDeleted)):
            del tmpList[elementsToBeDeleted[i]]
            
        return tmpList

def pretty_dictionary(dic):
    tab = PrettyTable(['key', 'value'])
    for key, val in dic.items():
        wrapped_value_lines = wrap(str(val) or '', VAL_WRAP_WIDTH) or ['']
        tab.add_row([key, wrapped_value_lines[0]])
        for subseq in wrapped_value_lines[1:]:
            tab.add_row(['', subseq])
    return tab