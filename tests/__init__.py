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
"""
TestCases for the REST API

Classes:
DomainTests --  /domain
ApplicationTests -- /domain/{NAME}/applications
ComponentTests -- /domain/{NAME}/applications/{ID}/components
DeviceManagerTests -- /domain/{NAME}/deviceManagers
DeviceTests -- /domain/{NAME}/deviceManagers/{ID}/devices
"""
__author__ = 'rpcanno'

from defaults import Default

from domain import DomainTests
from devicemanager import DeviceManagerTests
from device import DeviceTests
from application import ApplicationTests
from component import ComponentTests
from bulkio import BulkIOTests
from port import PortTests
