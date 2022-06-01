#!/bin/bash

# vars
rootdir=$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")
selfname=$(basename "$(readlink -f "${BASH_SOURCE[0]}")")
sessionname=$(echo "${selfname}" | cut -f1 -d".")
wbdir="${rootdir}/wurzelbot"
logdir="${rootdir}/log"
wblogdir="${logdir}/logs"
pydir="${wbdir}/functions"
tmpdir="${wbdir}/tmp"
datadir="${wbdir}/data"

# Check distribution
echo "Checking distribution..."

if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
    echo "$NAME $VERSION_ID is supported."
elif type lsb_release >/dev/null 2>&1; then
    OS=$(lsb_release -si)
    VER=$(lsb_release -sr)
    echo "$(lsb_release -si) $(lsb_release -sr) is supported."
elif [ -f /etc/lsb-release ]; then
    . /etc/lsb-release
    OS=$DISTRIB_ID
    VER=$DISTRIB_RELEASE
    echo "$DISTRIB_ID $DISTRIB_RELEASE is supported."
elif [ -f /etc/debian_version ]; then
    echo "Your OS is outdated and NOT supported! INSTALLATION FAILED!"
    exit
elif [ -f /etc/SuSe-release ]; then
    echo "Your OS is outdated and NOT supported! INSTALLATION FAILED!"
    exit
elif [ -f /etc/redhat-release ]; then
    echo "Your OS is outdated and NOT supported! INSTALLATION FAILED!"
    exit
else
    echo "Your OS is NOT supported (yet)!  INSTALLATION FAILED!"
    exit
fi


# Check root and deny if present
if [ "$(id -u)" = "0" ]; then
   echo "DO NOT RUN THIS SCRIPT AS ROOT!"
   exit
fi

# Check requirements

# Check for update if present else install