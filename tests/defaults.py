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
    RESOURCE_NOT_FOUND_MSG_REGEX = re.compile("^Unable to find .[^']* '.[^']*'$")