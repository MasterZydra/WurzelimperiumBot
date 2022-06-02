[![Python application](https://github.com/MasterZydra/WurzelimperiumBot/actions/workflows/python-app.yml/badge.svg)](https://github.com/MasterZydra/WurzelimperiumBot/actions/workflows/python-app.yml)
[![Python 3](https://img.shields.io/badge/python-3-blue.svg)](https://www.python.org/)
![GitHub](https://img.shields.io/github/license/MasterZydra/WurzelimperiumBot)

A forked from [MrFlamez/Wurzelimperium-Bot](https://github.com/MrFlamez/Wurzelimperium-Bot)

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

## Features
- Login ohne zusätzliche Verwendung eines Browsers
- Vollautomatische Bewässerung aller Gärten inkl. Wassergarten
- Automatisiertes Anpflanzen
- Abfrage aller aktuellen Marktpreise (Keine Abhängigkeit von Preislistenpflegern und deren Aktualisierungsintervall!)

## Installation
**Voraussetzung:** Python 3
1. Installation der Abhängigkeiten:  
`pip install -r ./requirements.txt`
2. Anmeldedaten im Skript hinterlegen (bei [example.py](./example.py) und [console.py](./console.py)).  
   Beim automatisierten Skript [automated_script.py](./automated_script.py) werden die Anmeldedaten beim Aufruf übergeben:  
   `python3 ./automated_script.py <server-nr> <username> <password>`
3. Skript ausführen

## Installationsskript für Linux
Das Installationsskript für Linux befindet sich im Branch [`unix`](https://github.com/MasterZydra/WurzelimperiumBot/tree/unix).  
Vielen Dank an [xRuffKez](https://github.com/xRuffKez) für die Entwicklung.
