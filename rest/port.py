"""
Rest handlers for Ports
"""

from tornado import web


class PortHandler(web.RequestHandler):

    def initialize(self, kind=None):
        self._kind = kind

    def get(self, *args):
        self.set_status(500)
        self.write(dict(status='Port handler for %s not implemented' % self._kind))