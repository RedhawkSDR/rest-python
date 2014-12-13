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
Rest handlers for Ports
"""

import logging
from tornado import web, ioloop
from helper import PortHelper
from model.domain import ResourceNotFound
from tornado import gen

import json

from handler import JsonHandler
from helper import PropertyHelper

class PortHandler(JsonHandler, PropertyHelper, PortHelper):

    def initialize(self, kind, redhawk=None, _ioloop=None):
        super(PortHandler, self).initialize(redhawk)
        self.kind = kind
        if not _ioloop:
            _ioloop = ioloop.IOLoop.current()
        self._ioloop = _ioloop

    @gen.coroutine
    def get(self, *args):
        try:
            logging.debug("port kind=%s, path=%s", self.kind, args)
            obj, path = yield self.redhawk.get_object_by_path(args, path_type=self.kind)
            logging.debug("Found object %s", dir(obj))
            if path:
                name = path[0]
                for port in obj.ports:
                    if port.name == name:
                        self.write(json.dumps(self.format_port(port)))
                        break
                else:
                    raise ResourceNotFound('port', name)
            else:
                self.write(json.dumps(self.format_ports(obj.ports)))
        except ResourceNotFound, e:
            logging.debug('Resource not found %s' % str(e), exc_info=1)
            self.set_status(404)
            self.write(dict(error='ResourceNotFound', message=str(e)))
        except Exception, e:
            logging.exception('Error with request %s' % self.request.full_url())
            self.set_status(500)
            self.write(dict(error='SystemError', message=str(e)))
