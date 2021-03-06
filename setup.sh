#!/bin/sh
#
# This file is protected by Copyright. Please refer to the COPYRIGHT file
# distributed with this source distribution.
#
# This file is part of REDHAWK rest-python.
#
# REDHAWK rest-python is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# REDHAWK rest-python is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#

# Absolute path to this script, e.g. /home/user/bin/foo.sh
SCRIPT=$(readlink -f "$0")
# Absolute path this script is in, thus /home/user/bin
SCRIPTPATH=$(dirname "$SCRIPT")

venv="${SCRIPTPATH}/.virtualenv"
pyvenv=${SCRIPTPATH}/pyvenv

case "$1" in

  install)
    if [ -d $venv ]; then
      echo "Removing old python virtualenv"
      rm -rf ${venv}
    fi

    virtualenv --system-site-packages ${venv}
    ${pyvenv} pip install -r requirements.txt
  ;;

  uninstall)
    if [ -d $venv ]; then
      echo "Removing old python virtualenv"
      rm -rf ${venv}
    fi
  ;;

  *)
    echo "Usage: $0 {install|uninstall}"
  ;;
esac
