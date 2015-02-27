__author__ = 'depew'

RHWEB_VERSION = '1.2.0'

from handler import JsonHandler

def _identify_remote_location_version(v):
    '''
    :param v: tuple representing version major, minor, patch
    :return: boolean
       >>> _identify_remote_location_version((1, 10, 2))
       False
       >>> _identify_remote_location_version((1, 10, 3))
       True
       >>> _identify_remote_location_version((1, 11, 1))
       True
       >>> _identify_remote_location_version((2, 1, 1))
       True
       >>> _identify_remote_location_version((1, 9, 3))
       False
    '''
    return (v[0] > 1) or \
           (v[0] == 1 and
               (v[1] == 10 and v[2] > 2) or
               (v[1] > 10))

    
def _parse_dist_version(distver, element=None):
    '''
    :param distver: distribution version from pkg_resources
    :return: a three element tuple of only the integers
        >>> _parse_dist_version(('00000001', '00000010', '00000002', '*final'))
        (1, 10, 2)
        >>> _parse_dist_version(('00000002', '00000012', '00000002', '*final'))
        (2, 12, 2)
        >>> _parse_dist_version(('00000002', '00000012', '0000002b', '*final'))
        (2, 12, 2)
        >>> _parse_dist_version(('00000002', '00000012', '000000b', '*final'))
        (2, 12, 0)
        >>> _parse_dist_version(('00000002', '00000012', 'b', '*final'))
        (2, 12, 0)
    '''
    if element is None:
        return (_parse_dist_version(distver, 0), 
                _parse_dist_version(distver, 1), 
                _parse_dist_version(distver, 2))
    try:
        return int(re.findall('\d+', distver[element])[0])
    except (ValueError, IndexError):
        return 0

class SysInfoHandler(JsonHandler):

    def get(self):
       self._render_json(self.redhawk.get_redhawk_info())
    
