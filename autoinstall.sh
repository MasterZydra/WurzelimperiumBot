#!/bin/bash
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
                                                                                                   

printf "\033c" # Meister Proper :D

printf "Checking sudo access... "
CAN_I_RUN_SUDO=$(sudo -n uptime 2>&1 | grep "load" | wc -l)
if [ ${CAN_I_RUN_SUDO} -gt 1 ]; then
    printf "FAIL\nYou have no sudo access, which is required for installing WurzelimperiumBot!\nINSTALLATION FAILED!\n"
    exit
else
    printf "OK\n"
fi

# vars
rootdir=$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")
selfname=$(basename "$(readlink -f "${BASH_SOURCE[0]}")")
sessionname=$(printf "${selfname}" | cut -f1 -d".")
wbdir="${rootdir}/wurzelbot"
logdir="${rootdir}/log"
wblogdir="${logdir}/logs"
confdir="${wbdir}/conf"
tmpdir="${wbdir}/tmp"
datadir="${wbdir}/data"
gituser="MasterZydra"
gitrepo="WurzelimperiumBot"
gitbranch="master"

# Check distribution
printf "Checking distribution...\n"

if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
    printf "$NAME $VERSION_ID is supported.\n"
elif type lsb_release >/dev/null 2>&1; then
    OS=$(lsb_release -si)
    VER=$(lsb_release -sr)
    printf "$(lsb_release -si) $(lsb_release -sr) is supported.\n"
elif [ -f /etc/lsb-release ]; then
    . /etc/lsb-release
    OS=$DISTRIB_ID
    VER=$DISTRIB_RELEASE
    printf "$DISTRIB_ID $DISTRIB_RELEASE is supported.\n"
elif [ -f /etc/debian_version ]; then
    printf "Your OS is outdated and NOT supported!\nINSTALLATION FAILED!\n"
    exit
elif [ -f /etc/SuSe-release ]; then
    printf "Your OS is outdated and NOT supported!\nINSTALLATION FAILED!\n"
    exit
elif [ -f /etc/redhat-release ]; then
    printf "Your OS is outdated and NOT supported!\nINSTALLATION FAILED!\n"
    exit
else
    printf "Your OS is NOT supported (yet)!\nINSTALLATION FAILED!\n"
    exit
fi


# Check root and deny if present
if [ "$(id -u)" = "0" ]; then
   printf "DO NOT RUN THIS SCRIPT AS ROOT!\nINSTALLATION FAILED!\n"
   exit
fi

# Check requirements
printf "Checking requirements...\n"
version=$(python3 -V 2>&1 | grep -Po '(?<=Python )(.+)')
if [[ -z "$version" ]]; then
    printf "Python3 not found. Installing....\n"
    sudo apt update
    sudo apt -y install software-properties-common
    #PPA for Python3.X
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt install -y python3.9
    if [[ -z "$version" ]]; then
        printf "An Error occured when installing Python3! Please manually install it and run the installer again!\nINSTALLATION FAILED!\n" 
        exit
    else
        printf "Python3 installed successfully.\n"
    fi
else
    printf "Python3 found.\n" 
fi
sudo apt install -y git

# Clone from master
printf "Cleaning temp files.\n"
rm -rf "${tmpdir}"
rm -rf "${datadir}"
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
pip install --upgrade pip
pip install -r "${datadir}"/requirements.txt

# Creating worker
[ ! -f "${rootdir}"/worker.sh ] && touch "${rootdir}"/worker.sh && chmod +x "${rootdir}"/worker.sh

cat <<EOT >> "${rootdir}"/worker.sh
#!/bin/bash
# Script written by xRuffKez for WurzelimperiumBot by MrFlamez & MasterZydra

while true
do 

    conf='${confdir}/acc.conf'
    while read -r line; do
        [[ "\$line" =~ ^#.*$ ]] && continue
        python3 ${datadir}/automated_script.py "\${line}"
    done < "\$conf"
    sleep 60
done
EOT