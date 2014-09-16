#!/bin/sh

# Absolute path to this script, e.g. /home/user/bin/foo.sh
SCRIPT=$(readlink -f "$0")
# Absolute path this script is in, thus /home/user/bin
SCRIPTPATH=$(dirname "$SCRIPT")
pyvenv="${SCRIPTPATH}/pyvenv"

source /etc/profile.d/redhawk.sh

exec ${pyvenv} python ${SCRIPTPATH}/pyrest.py $@
