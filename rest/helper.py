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
        port_dict = []
        for port in ports:
            port_value = {'name': port.name, 'direction': port._direction}
            if port._direction == 'Uses':
                port_value['type'] = port._using.name
                port_value['namespace'] = port._using.nameSpace
            port_dict.append(port_value)
        return port_dict
