"""
Rest handlers for Waveforms

Classes:
Waveforms -- Get info, launch and release
"""

from handler import JsonHandler
from helper import PropertyHelper, PortHelper
from model.domain import Domain

import json


class Waveforms(JsonHandler, PropertyHelper, PortHelper):

    def get(self, domain_name, app_id=None):
        dom = Domain(str(domain_name))

        if app_id:
            app = dom.find_app(app_id)

            info =  {
                'id': app._get_identifier(),
                'name': app.name,
                'started': app._get_started(),
                'components': dom.components(app_id),
                'ports': self.format_ports(app.ports),
                'properties': self.format_properties(app._properties)
            }
        else:
            info = {'waveforms': dom.apps(), 'available': dom.available_apps()}

        self._render_json(info)

    def post(self, domain_name, app_id=None):
        data = json.loads(self.request.body)
        dom = Domain(str(domain_name))

        if app_id:
            app = dom.find_app(app_id)

            started = data['started']
            if started:
                app.start()
            else:
                app.stop()

            self._render_json({'id': app_id, 'started': app._get_started()})
        else:
            app_name = data['name']

            app_id = dom.launch(str(app_name))

            if 'started' in data and data['started']:
                app = dom.find_app(app_id)
                app.start()

            self._render_json({'launched': app_id, 'waveforms': dom.apps()})

    def put(self, domain_name, app_id=None):
        data = json.loads(self.request.body)

        dom = Domain(str(domain_name))
        app = dom.find_app(app_id)

        started = data['started']
        if started:
            app.start()
        else:
            app.stop()

        self._render_json({'id': app_id, 'started': app._get_started()})

    def delete(self, domain_name, app_id):
        dom = Domain(str(domain_name))
        dom.release(app_id)

        self._render_json({'released': app_id, 'waveforms': dom.apps()})