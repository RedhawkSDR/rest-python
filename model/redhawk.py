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
    redhawk.py

    Asynchronous Tornado service for REDHAWK. Maps the functions
    in domain.py and caches the domain object.
"""

from _utils.tasking import background_task

from domain import Domain, scan_domains


class Redhawk(object):
    __domains = {}

    def _get_domain(self, domain_name):
        name = str(domain_name)
        # if not name in self.__domains:
        #     self.__domains[name] = Domain(domain_name)
        #
        # return self.__domains[name]
        return Domain(domain_name)

    ##############################
    # DOMAIN

    @background_task
    def get_domain_list(self):
        return scan_domains()

    @background_task
    def get_domain_info(self, domain_name):
        dom = self._get_domain(domain_name)
        return dom.get_domain_info()

    @background_task
    def get_domain_properties(self, domain_name):
        dom = self._get_domain(domain_name)
        return dom.properties()

    ##############################
    # APPLICATION

    @background_task
    def get_application(self, domain_name, app_id):
        dom = self._get_domain(domain_name)
        return dom.find_app(app_id)

    @background_task
    def get_application_list(self, domain_name):
        dom = self._get_domain(domain_name)
        return dom.apps()

    @background_task
    def get_available_applications(self, domain_name):
        dom = self._get_domain(domain_name)
        return dom.available_apps()

    @background_task
    def launch_application(self, domain_name, app_name):
        dom = self._get_domain(domain_name)
        return dom.launch(app_name)

    @background_task
    def release_application(self, domain_name, app_id):
        dom = self._get_domain(domain_name)
        return dom.release(app_id)

    ##############################
    # COMPONENT

    @background_task
    def get_component(self, domain_name, app_id, comp_id):
        dom = self._get_domain(domain_name)
        return dom.find_component(app_id, comp_id)

    @background_task
    def get_component_list(self, domain_name, app_id):
        dom = self._get_domain(domain_name)
        return dom.components(app_id)

    @background_task
    def component_configure(self, domain_name, app_id, comp_id, new_properties):
        dom = self._get_domain(domain_name)
        comp = dom.find_component(app_id, comp_id)

        configure_changes = {}
        for prop in comp._properties:
            if prop.id in new_properties:
                if new_properties[prop.id] != prop.queryValue():
                    configure_changes[prop.id] = (type(prop.queryValue()))(new_properties[prop.id])

        return comp.configure(configure_changes)

    ##############################
    # DEVICE MANAGER

    @background_task
    def get_device_manager(self, domain_name, device_manager_id):
        dom = self._get_domain(domain_name)
        return dom.find_device_manager(device_manager_id)

    @background_task
    def get_device_manager_list(self, domain_name):
        dom = self._get_domain(domain_name)
        return dom.device_managers()

    ##############################
    # DEVICE

    @background_task
    def get_device_list(self, domain_name, device_manager_id):
        dom = self._get_domain(domain_name)
        return dom.devices(device_manager_id)

    @background_task
    def get_device(self, domain_name, device_manager_id, device_id):
        dom = self._get_domain(domain_name)
        return dom.find_device(device_manager_id, device_id)

    ##############################
    # SERVICE

    @background_task
    def get_service_list(self, domain_name, device_manager_id):
        dom = self._get_domain(domain_name)
        return dom.services(device_manager_id)
