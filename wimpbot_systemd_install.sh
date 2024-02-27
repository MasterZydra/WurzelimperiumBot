#!/bin/bash
# shellcheck disable=SC1091
#
# Script written by xRuffKez for WurzelimperiumBot by MrFlamez & MasterZydra
# PS: Tot den Maulwürfen!

# __          __                 _ _                           _                   ____        _    
# \ \        / /                | (_)                         (_)                 |  _ \      | |   
#  \ \  /\  / /   _ _ __ _______| |_ _ __ ___  _ __   ___ _ __ _ _   _ _ __ ___   | |_) | ___ | |_  
#   \ \/  \/ / | | | '__|_  / _ \ | | '_ ` _ \| '_ \ / _ \ '__| | | | | '_ ` _ \  |  _ < / _ \| __| 
#    \  /\  /| |_| | |   / /  __/ | | | | | | | |_) |  __/ |  | | |_| | | | | | | | |_) | (_) | |_  
#     \/  \/  \__,_|_|  /___\___|_|_|_| |_| |_| .__/ \___|_|  |_|\__,_|_| |_| |_| |____/ \___/ \__| 
#                                             | |                                                   
#                                             |_|                                                   
#         _____           _        _ _              __             _      _                         
#        |_   _|         | |      | | |            / _|           | |    (_)                        
#          | |  _ __  ___| |_ __ _| | | ___ _ __  | |_ ___  _ __  | |     _ _ __  _   ___  __       
#          | | | '_ \/ __| __/ _` | | |/ _ \ '__| |  _/ _ \| '__| | |    | | '_ \| | | \ \/ /       
#         _| |_| | | \__ \ || (_| | | |  __/ |    | || (_) | |    | |____| | | | | |_| |>  <        
#        |_____|_| |_|___/\__\__,_|_|_|\___|_|    |_| \___/|_|    |______|_|_| |_|\__,_/_/\_\       
#
#   SYSTEMD & APT EDITION                                                                                                  
#

# vars
rootdir=$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")
wbdir="${rootdir}/wurzelbot"
confdir="${wbdir}/conf"
tmpdir="${wbdir}/tmp"
datadir="${wbdir}/data"
gituser="MasterZydra"
gitrepo="WurzelimperiumBot"
gitbranch="master"

# Distribution und Version erkennen
distribution=$(lsb_release -si)
version=$(lsb_release -sr)

# Unterstützte Distributionen und Versionen definieren
supported_distributions=("Debian" "Ubuntu")
supported_versions=("11" "12" "20.04" "20.10" "22.04" "22.10")

# Überprüfen, ob die Distribution und Version unterstützt werden
if [[ ! " ${supported_distributions[@]} " =~ " ${distribution} " ]] || \
   [[ ! " ${supported_versions[@]} " =~ " ${version} " ]]; then
    echo "Dieses Skript ist für ${distribution} ${version} nicht kompatibel."
    exit 1
fi

# Paketmanager und -befehle je nach Distribution festlegen
case $distribution in
    "Debian")
        install_command="apt-get install -y"
        ;;
    "Ubuntu")
        install_command="apt install -y"
        ;;
esac

# Prüfen, ob das Skript als Root ausgeführt wird
if [ "$(id -u)" = "0" ]; then
    echo "Führen Sie dieses Skript nicht als Root aus!"
    exit 1
fi

# Prüfen, ob sudo-Zugriff vorhanden ist
if ! sudo -n true 2>/dev/null; then
    echo "Sie haben keinen sudo-Zugriff, der für die Installation erforderlich ist!"
    exit 1
fi

# Pakete installieren
echo "Installiere erforderliche Pakete..."
sudo $install_command python3 python3-pip git || exit 1

# Temporäre Dateien löschen und Verzeichnisse erstellen
echo "Temporäre Dateien löschen und Verzeichnisse erstellen..."
rm -rf "$tmpdir" "$datadir"
mkdir -p "$wbdir" "$datadir" "$tmpdir" "$confdir"

# Konfigurationsdatei erstellen, wenn sie nicht existiert
echo "Konfigurationsdatei erstellen..."
acc_conf="$confdir/acc.conf"
if [ ! -f "$acc_conf" ]; then
    touch "$acc_conf"
    cat <<EOF > "$acc_conf"
# SERVERNR USERNAME PASSWORT
# KEINE RAUTE (#) davor setzen!!! Beispiel: 12 Hildegart camping2016
EOF
fi

# WurzelimperiumBot-Repository klonen
echo "WurzelimperiumBot-Repository klonen..."
git clone https://github.com/"${gituser}"/"${gitrepo}".git --depth 1 --branch="${gitbranch}" "$tmpdir" || exit 1
mv "$tmpdir"/* "$datadir" && rm -rf "$tmpdir"

# Python-Anforderungen installieren
echo "Python-Anforderungen installieren..."
pip3 install --upgrade pip || exit 1
pip3 install -r "${datadir}/requirements.txt" || exit 1

# Worker-Skript erstellen
echo "Worker-Skript erstellen..."
worker_script="$rootdir/worker.sh"
if [ ! -f "$worker_script" ]; then
    cat <<'EOF' > "$worker_script"
#!/bin/bash
# Script written by xRuffKez for WurzelimperiumBot by MrFlamez & MasterZydra

##
# Hier die die Zeit in Sekunden eintragen, wann der Bot automatisch arbeiten soll!
# Unter 60 secs nicht empfohlen (Gefahr gebannt zu werden!)
# timer=60
timer=60
##

while true; do
    conf="$confdir/acc.conf"
    while read -r line; do
        [[ "$line" =~ ^#.*$ ]] && continue
        python3 "${datadir}/automated_script.py" "$line"
    done < "$conf"
    sleep "$timer"
done
EOF
    chmod +x "$worker_script"
fi

# systemd-Dienst erstellen und starten
echo "systemd-Dienst erstellen und starten..."
cat <<EOF | sudo tee "/lib/systemd/system/wimpbot.service" >/dev/null
[Unit]
Description=WurzelimperiumBot

[Service]
Type=simple
User=$(id -un)
Group=$(id -gn)
WorkingDirectory=$rootdir
ExecStart=$worker_script

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload || exit 1
sudo systemctl enable wimpbot || exit 1
sudo systemctl start wimpbot || exit 1

# Installation abschließen
echo "Installation abgeschlossen!"
echo "Bitte konfigurieren Sie die Datei acc.conf im Verzeichnis conf."
