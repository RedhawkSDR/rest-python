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
Rest handlers

Classes:
JsonHandler -- Handle generic functions of a json rest interface
"""
import logging
import tornado.web
from model.domain import ResourceNotFound


class JsonHandler(tornado.web.RequestHandler):
    redhawk = None

    def initialize(self, redhawk):
        self.redhawk = redhawk

    def _handle_request_exception(self, e):
        logging.error('Exception:: %s', e, exc_info=1)

        status = 500
        resp = {'message': str(e), 'error': type(e).__name__}

        if type(e) == ResourceNotFound:
            status = 404
        elif type(e) == KeyError:
            resp = {'error': 'JsonParsing', 'message': "Expecting value "+str(e)}
        elif type(e) == ValueError:
            resp = {'error': 'JsonParsing', 'message': str(e)}

        self._render_error(resp, status)

    def _render_json(self, resp):
        if resp and not 'error' in resp:
            self.set_header("Content-Type", "application/json; charset='utf-8'")
            self.write(resp)
        else:
            self._render_error("Unable to find requested resource", 404)

    def _render_error(self, msg, status=500):
        self.set_status(status)
        self.finish(msg)
