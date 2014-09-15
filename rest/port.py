"""
Rest handlers for Ports
"""

import logging
from tornado import web, ioloop
from helper import PortHelper
from model.domain import Domain, ResourceNotFound
import json


class PortHandler(web.RequestHandler, PortHelper):

    def initialize(self, kind, _ioloop=None):
        self.kind = kind
        if not _ioloop:
            _ioloop = ioloop.IOLoop.current()
        self._ioloop = _ioloop

    def get(self, *args):
        try:
            logging.debug("port kind=%s, path=%s", self.kind, args)
            obj, path = Domain.locate_by_path(args, path_type=self.kind)
            logging.debug("Found object %s", dir(obj))
            if path:
                self.write(json.dumps(self.format_port(obj.getPort(path[0]))))
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