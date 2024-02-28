[![Python application](https://github.com/MasterZydra/WurzelimperiumBot/actions/workflows/python-app.yml/badge.svg)](https://github.com/MasterZydra/WurzelimperiumBot/actions/workflows/python-app.yml)
[![Python 3](https://img.shields.io/badge/python-3-blue.svg)](https://www.python.org/)
![GitHub](https://img.shields.io/github/license/MasterZydra/WurzelimperiumBot)
[![WurzelimperiumBot Binary Compile and Release](https://github.com/MasterZydra/WurzelimperiumBot/actions/workflows/release2binary.yml/badge.svg?event=release)](https://github.com/MasterZydra/WurzelimperiumBot/actions/workflows/release2binary.yml)

A forked from [MrFlamez/Wurzelimperium-Bot](https://github.com/MrFlamez/Wurzelimperium-Bot)

*Read this in other languages: [English](README.md), [German](README.de.md).*

# Wurzelimperium-Bot
Ein Bot für das Browserspiel Wurzelimperium von Upjers. Mit ihm wird es den kostenlosen Spielern ermöglicht die Vorzüge eines Premiumaccounts zu nutzen.

**Inhaltsverzeichnis**
- [Verwendung](#verwendung)
- [Features](#features)
- [Installation](#installation)
- [Installationsskript für Linux](#installationsskript-für-linux)

## Verwendung
Die Nutzung des Bots ist über verschiedene Arten möglich:
- **Skript**:  
Wie in [example.py](./example.py) kann die Aufgabe als Skript erstellt und manuell auf dem PC ausgeführt werden.
- **Automatisiert**:  
Ähnlich wie beim Skript kann eine komplexeres Skript erstellt werden, welches beispielsweise durch GitHub Actions zyklisch ausgeführt wird. Siehe [automated_script.py](./automated_script.py)
- **Interaktiv**:  
Über das Programm [console.py](./console.py) kann über Eingaben wie zum Beispiel `water` der gesamte Garten bewässert werden.

Für die Verwendung ist jeweils das Hinterlegen von der Servernummer, dem Benutzernamen und des Passworts in den Dateien notwendig.

- **Standalone**:
Es gibt auch eine portable Windows Commandline Version ohne Vorraussetzungen. [Win32-CLI-Standalone](https://github.com/MasterZydra/WurzelimperiumBot/releases/)

## Features
- Login ohne zusätzliche Verwendung eines Browsers
- Vollautomatische Bewässerung aller Gärten inkl. Wassergarten
- Automatisiertes Anpflanzen
- Abfrage aller aktuellen Marktpreise (Keine Abhängigkeit von Preislistenpflegern und deren Aktualisierungsintervall!)
- Automatische Abfertigung der Wimps in den Gärten. Der minimale Bestand kann in den Account-Notizen eingestellt werden. z. B. `minStock: 100` oder `minStock(Apfel): 200`
- Automatisches claimen des täglichen Login Bonus

## Installation
**Voraussetzung:** [Python 3](https://www.python.org/download/releases/3.0/)
1. Installation der Abhängigkeiten:  
`pip install -r ./requirements.txt`
2. Anmeldedaten im Skript hinterlegen (bei [example.py](./example.py) und [console.py](./console.py)).  
   Beim automatisierten Skript [automated_script.py](./automated_script.py) werden die Anmeldedaten beim Aufruf übergeben: </br>
   `python3 ./automated_script.py <server-nr> <username> <password> <lang>` </br>
   Beispiel: python3 ./automated_script.py 12 MaulwurfEddie passwort1337 de
3. Skript ausführen

## Installationsskript für Linux
Das Installationsskript für Linux befindet sich im Branch [`unix`](https://github.com/MasterZydra/WurzelimperiumBot/tree/unix).  
Vielen Dank an [xRuffKez](https://github.com/xRuffKez) für die Entwicklung.
