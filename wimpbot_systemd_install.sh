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
grp="$(id -g)"
usr="$(whoami)"
wbdir="${rootdir}/wurzelbot"
confdir="${wbdir}/conf"
tmpdir="${wbdir}/tmp"
datadir="${wbdir}/data"
gituser="MasterZydra"
gitrepo="WurzelimperiumBot"
gitbranch="master"

printf "\033c" # Meister Proper :D

# Check root and deny if present
if [ "$(id -u)" = "0" ]; then
   printf "DO NOT RUN THIS SCRIPT AS ROOT!\nINSTALLATION FAILED!\n"
   exit
fi

printf "Checking sudo access... "
su=$(sudo -n uptime 2>&1 | grep -c "load")
if [ "${su}" -gt 1 ]; then
    printf "FAIL\nYou have no sudo access, which is required for installing WurzelimperiumBot!\nINSTALLATION FAILED!\n"
    exit
else
    printf "OK\n"
fi

# Check distribution
printf "Checking distribution...\n"

if [ -f /etc/os-release ]; then
    . /etc/os-release
    printf "%s is supported.\n" "$NAME $VERSION_ID"
elif type lsb_release >/dev/null 2>&1; then
    printf "%s is supported.\n" "$(lsb_release -si) $(lsb_release -sr)"
elif [ -f /etc/lsb-release ]; then
    . /etc/lsb-release
    printf "%s is supported.\n" "$DISTRIB_ID $DISTRIB_RELEASE"
else
    printf "Your OS is NOT supported!\nINSTALLATION FAILED!\n"
    exit
fi


# Check requirements
printf "Checking requirements...\n"
sudo apt update && sudo apt -y upgrade && sudo apt install -y python3 && sudo apt install -y pip && sudo apt install -y git

# Clone from master
printf "Cleaning temp files.\n"
rm -rf "${tmpdir}" && rm -rf "${datadir}"
printf "Checking directories and creating them if needed.\n"
[ ! -d "${wbdir}" ] && mkdir "${wbdir}"
[ ! -d "${datadir}" ] && mkdir "${datadir}"
[ ! -d "${tmpdir}" ] && mkdir "${tmpdir}"
[ ! -d "${confdir}" ] && mkdir "${confdir}"
[ ! -f "${confdir}"/acc.conf ] && touch "${confdir}"/acc.conf && echo "# SERVERNR USERNAME PASSWORT" >> "${confdir}"/acc.conf && echo "# KEINE RAUTE (#) davor setzen!!! Beispiel: 12 Hildegart camping2016" >> "${confdir}"/acc.conf 

printf "Retrieving files for WurzelimperiumBot.\n"
git clone https://github.com/"${gituser}"/"${gitrepo}".git --depth 1 --branch="${gitbranch}" "${tmpdir}"
mv "${tmpdir}"/* "${datadir}" && rm -rf "${tmpdir}"

# Install py requirements with pip
pip install --upgrade pip && pip install -r "${datadir}"/requirements.txt

# Creating worker
[ ! -f "${rootdir}"/worker.sh ] && touch "${rootdir}"/worker.sh && chmod +x "${rootdir}"/worker.sh

cat <<EOT >> "${rootdir}"/worker.sh
#!/bin/bash
# Script written by xRuffKez for WurzelimperiumBot by MrFlamez & MasterZydra

##
# Hier die die Zeit in Sekunden eintragen, wann der Bot automatisch arbeiten soll!
# Unter 60 secs nicht empfohlen (Gefahr gebannt zu werden!)
# timer=60
timer=60
##


while true
do 

    conf='${confdir}/acc.conf'
    while read -r line; do
        [[ "\$line" =~ ^#.*$ ]] && continue
        python3 ${datadir}/automated_script.py \${line}
    done < "\$conf"
    sleep "\$timer"
done
EOT

# Creating systemd service
sudo systemctl stop wimpbot && sudo systemctl disable wimpbot && sudo rm /lib/systemd/system/wimpbot.service && sudo touch /lib/systemd/system/wimpbot.service

cat <<EOT >> "${rootdir}"/wimpbot.service
[Unit]
Description=WurzelimperiumBot

[Service]
Type=simple
User=${usr}
Group=${grp}
WorkingDirectory=${rootdir}
ExecStart=${rootdir}/worker.sh

[Install]
WantedBy=multi-user.target
EOT
sudo mv "${rootdir}"/wimpbot.service /lib/systemd/system/wimpbot.service && sudo systemctl daemon-reload  && sudo systemctl enable wimpbot && sudo systemctl start wimpbot
printf "\033c" # Meister Proper :D
sudo systemctl status wimpbot
printf "\n\n\nInstallation finished!\n\nPlease configure acc.conf in the conf directory!\n\n"
