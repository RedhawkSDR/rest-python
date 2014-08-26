__author__ = 'rpcanno'

import re


class Default(object):
    REST_BASE = "/rh/rest"
    DOMAIN_NAME = "REDHAWK_DEV"

    WAVEFORM = 'SigTest'
    COMPONENT = 'SigGen'

    RESOURCE_NOT_FOUND_ERR = 'ResourceNotFound'
    RESOURCE_NOT_FOUND_MSG_REGEX = re.compile("^Unable to find .[^']* '.[^']*'$")