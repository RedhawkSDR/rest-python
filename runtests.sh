#!/bin/sh -e
# Runs the unit test with nose in the virtual environment

err() {
    echo "ERROR: $@" 1>&2
    exit 1
}

. /usr/libexec/sdrtools/sdrlib.bash || err "Unable to load sdrlib bash library"

COMPONENTS="KitchenSink SigGen"
WAVEFORMS="SigTest TestConfigureWaveform"

# verify the components
for c in $COMPONENTS ; do
    st_verify_component "$c" || err "Missing component '$c'"
done

# verify the waveforms
for c in $WAVEFORMS ; do
    st_verify_waveform "$c" || err "Missing waveform '$c'"
done


#trap 'rhkill.sh -1' 0 1

#rhkill.sh -2

# Domain Manager
#nodeBooter $NBARGS -D /domain/DomainManager.dmd.xml --domainname $RHDOMAIN || exit 1 &

#sleep 2
# GPP
#nodeBooter $NBARGS -d /nodes/GPP/DeviceManager.dcd.xml  --domainname $RHDOMAIN || exit 1 &

#sleep 4
#.virtualenv/bin/python /usr/bin/nosetests1.1 --with-doctest --with-coverage --where . --where model/ --where tests/ --where rest --cover-tests "$@"  2>&1 | tee tests.out

# example test:Sysinfo

if [ $# -lt 1 ] ; then
    set -- test
fi
.virtualenv/bin/python /usr/bin/nosetests1.1 --with-doctest --with-coverage --cover-tests "$@"  2>&1 | tee tests.out
