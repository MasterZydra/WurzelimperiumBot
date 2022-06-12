


# WurzelimperiumBot Installskript für Linux
Ein Script, das einen Bot für das Browserspiel Wurzelimperium von Upjers auf Unix Systemen installiert.

Installiert automatisch den WurzelimperiumBot und führt diesen jede Minute aus. Dank der Konfiguration, kann dieser mit Accounts erweitert werden.


# Unterstützte Distributionen

Alle Systemd Distros mit APT Paketmanager:

- Ubuntu LTS 20.04/22.04 (getestet, point-releases sollten auch funktionieren)
- Debian 10/11 (getestet mit Bullseye, sollte entsprechend auch mit Buster funktionieren)


# Installation

- Downloade das Skript:

```wget https://raw.githubusercontent.com/MasterZydra/WurzelimperiumBot/unix/wimpbot_systemd_install.sh```

- Das Skript ausführbar machen mit dem Benutzer auf dem der Bot später laufen soll:

```chmod +x wimpbot_systemd_install.sh```

- Vorab sich mit sudo authentifizieren:

```sudo -v```

- Führe das Skript nun aus (bitte NICHT mit root oder sudo!!!).

```./wimpbot_systemd_install.sh```

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

Beachte bitte dabei den service neu zu starten!
```sudo systemctl restart wimpbot```

# Update

Um den WurzelimperiumBot zu updaten, führe einfach die wimpbot_systemd_install.sh aus.
