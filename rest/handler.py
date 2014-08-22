"""
Rest handlers

Classes:
JsonHandler -- Handle generic functions of a json rest interface
"""

import tornado.web
from model.domain import ResourceNotFound


class JsonHandler(tornado.web.RequestHandler):
    def _handle_request_exception(self, e):
        print 'Exception::', e

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
