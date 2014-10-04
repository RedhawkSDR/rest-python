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
