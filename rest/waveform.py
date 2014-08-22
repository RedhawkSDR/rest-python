"""
Rest handlers for Waveforms

Classes:
Waveforms -- Get info, launch and release
"""

from handler import JsonHandler
from model.domain import Domain

import json


class Waveforms(JsonHandler):

    def get(self, domain_name, app_id=None):
        dom = Domain(str(domain_name))

        if app_id:
            info = dom.app_info(app_id)
        else:
            info = {'waveforms': dom.apps(), 'available': dom.available_apps()}

        self._render_json(info)

    def post(self, domain_name):
        data = json.loads(self.request.body)

        app_name = data['name']

        dom = Domain(str(domain_name))
        app_id = dom.launch(app_name)

        self._render_json({'launched': app_id, 'waveforms': dom.apps()})

    def delete(self, domain_name, app_id):
        dom = Domain(str(domain_name))
        dom.release(app_id)

        self._render_json({'released': app_id, 'waveforms': dom.apps()})