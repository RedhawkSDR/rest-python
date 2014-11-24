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
Provides static classes to format for REST

Classes:
PropertyHelper -- Convert CORBA and RH Sandbox Properties into dictionaries (more descriptive than prop_to_dict)
PortHelper -- Convert Port information into dict
"""

from ossie.utils.prop_helpers import Property


class PropertyHelper(object):

    @staticmethod
    def format_properties(properties):
        if not properties:
            return []
        elif any(isinstance(p, Property) for p in properties):
            return PropertyHelper._property_set(properties)
        else:
            return PropertyHelper._corba_properties(properties)

    @staticmethod
    def _corba_properties(properties):
        prop_dict = []
        for prop in properties:
            ret = PropertyHelper.__any(prop.value)
            ret['id'] = prop.id
            prop_dict.append(ret)

        return prop_dict

    @staticmethod
    def _property_set(properties):
        prop_dict = []
        for prop in properties:
            if prop.type != 'struct' and prop.type != 'structSeq':
                if isinstance(prop.queryValue(), list):
                    prop_type = "simpleSeq"
                else:
                    prop_type = 'simple'
            else:
                prop_type = prop.type

            prop_json = {
                'id': prop.id,
                'name': prop.clean_name,
                'value': prop.queryValue(),
                'scaType': prop_type,
                'mode': prop.mode,
                'kinds': prop.kinds
            }

            if prop_type == 'simple':
                prop_json['type'] = type(prop.queryValue()).__name__
                if prop_json['type'] == 'str':
                    prop_json['type'] = 'string'
                elif prop_json['type'] == 'bool':
                    prop_json['type'] = 'boolean'

            if '_enums' in dir(prop) and prop._enums:
                prop_json['enumerations'] = prop._enums

            prop_dict.append(prop_json)
        return prop_dict

    ###############################################
    # Private

    @staticmethod
    def __any_simple(corba_any):
        return {'scaType': 'simple', 'value': corba_any._v}

    @staticmethod
    def __any_struct(corba_any):
        ret = {'scaType': 'struct'}
        value = {}
        for a in corba_any._v:
            value[a.id] = a.value._v
        ret['value'] = value
        return ret

    @staticmethod
    def __any_seq(corba_any):
        ret = {'scaType': 'seq', 'value': []}
        for a in corba_any._v:
            ret['value'].append(PropertyHelper.__any(a))
        return ret

    @staticmethod
    def __any(corba_any):
        type_name = str(corba_any._t)

        if 'CORBA.TypeCode("IDL:CF/Properties:1.0")' == type_name:
            return PropertyHelper.__any_struct(corba_any)
        elif 'CORBA.TypeCode("IDL:omg.org/CORBA/AnySeq:1.0")' == type_name:
            return PropertyHelper.__any_seq(corba_any)
        else:
            return PropertyHelper.__any_simple(corba_any)


class PortHelper(object):

    @staticmethod
    def format_ports(ports):
        return [PortHelper.format_port(port) for port in ports]

    @staticmethod
    def format_port(port):
        port_value = {'name': port.name, 'direction': port._direction}
        if port._direction == 'Uses':
            version_idx = port._using.repoId.rfind(':')
            version = port._using.repoId[version_idx:]

            port_value['repId'] = port._using.repoId
            port_value['idl'] = {
                'type': port._using.name,
                'namespace': port._using.nameSpace,
                'version': version
            }
        return port_value
