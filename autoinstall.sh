#!/bin/bash
# Script written by xRuffKez for WurzelimperiumBot by MrFlamez & MasterZydra
# PS: Tot den Maulwürfen!

# Meister Proper :D
printf "\033c"

# vars
rootdir=$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")
selfname=$(basename "$(readlink -f "${BASH_SOURCE[0]}")")
sessionname=$(printf "${selfname}" | cut -f1 -d".")
wbdir="${rootdir}/wurzelbot"
logdir="${rootdir}/log"
wblogdir="${logdir}/logs"
pydir="${wbdir}/functions"
tmpdir="${wbdir}/tmp"
datadir="${wbdir}/data"

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
    printf "$DISTRIB_ID $DISTRIB_RELEASE is supported."
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

# Check for update if present else install