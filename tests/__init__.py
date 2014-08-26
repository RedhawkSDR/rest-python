"""
TestCases for the REST API

Classes:
DomainTests --  /domain
WaveformTests -- /domain/{NAME}/waveforms
ComponentTests -- /domain/{NAME}/waveforms/{ID}/components
DeviceManagerTests -- /domain/{NAME}/deviceManagers
DeviceTests -- /domain/{NAME}/deviceManagers/{ID}/devices
"""
__author__ = 'rpcanno'

from defaults import Default

from domain import DomainTests
from devicemanager import DeviceManagerTests
from device import DeviceTests
from waveform import WaveformTests
from component import ComponentTests