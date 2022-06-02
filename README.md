


# WurzelimperiumBot Installskript für Linux
Ein Script, das einen Bot für das Browserspiel Wurzelimperium von Upjers auf Unix Systemen installiert.

Installiert automatisch den WurzelimperiumBot und führt diesen jede Minute aus. Dank der Konfiguration, kann dieser mit Accounts erweitert werden.


# Unterstützte Distributionen

Alle Systemd Distros mit APT Paketmanager:

- Ubuntu LTS 20.04/22.04 (getestet, point-releases sollten auch funktionieren)
- Debian 10/11 (ungetestet)


# Installation

- Downloade das Skript:

```wget https://raw.githubusercontent.com/MasterZydra/WurzelimperiumBot/unix/autoinstall.sh```

- Das Skript ausführbar machen mit dem Benutzer auf dem der Bot später laufen soll:

```chmod +x autoinstall.sh```

- Führe das Skript nun mit sudo aus (bitte NICHT mit root!!!).

```sudo ./autoinstall.sh```

- Nun editiere die acc.conf in ./wurzelbot/conf/acc.conf

```nano ./wurzelbot/conf/acc.conf```

Und füge deine Accountdaten ein.

```
# SERVERNR USERNAME PASSWORT
# KEINE RAUTE (#) davor setzen!!! Beispiel: 12 Hildegart camping2016
2 Julius pantoffel13
43 CarlosDerGärtner supderschwerespasswort2022
```

- Du kannst auch das Intervall ändern wann der Bot seine Aufgaben ausführen soll. Editiere dazu die worker.sh