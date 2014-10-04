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
__author__ = 'rpcanno'

import re


class Default(object):
    REST_BASE = "/rh/rest"
    DOMAIN_NAME = "REDHAWK_DEV"

    WAVEFORM = 'SigTest'

    COMPONENT = 'SigGen'
    COMPONENT_PROPERTY = 'frequency'
    COMPONENT_PROPERTY_VALUE = 1000
    COMPONENT_PROPERTY_CHANGE = 2000

    RESOURCE_NOT_FOUND_ERR = 'ResourceNotFound'
    RESOURCE_NOT_FOUND_MSG_REGEX = re.compile(r"^Unable to find .[^']* '.[^']*'$")
