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

# Check requirements

# Check root and deny if present

# Check for update if present else install