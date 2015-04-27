#!/bin/sh -e
# Runs the unit test with nose in the virtual environment
export RHDOMAIN=REDHAWK_TEST

NBARGS=--nopersist

# Domain Manager
nodeBooter $NBARGS -D /domain/DomainManager.dmd.xml --domainname $RHDOMAIN || exit 1 &

sleep 2

# GPP
nodeBooter $NBARGS -d /nodes/GPP/DeviceManager.dcd.xml  --domainname $RHDOMAIN || exit 1 &

