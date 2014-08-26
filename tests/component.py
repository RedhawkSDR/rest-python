"""
Tornado tests for the /domain/{NAME}/waveforms/{ID}/component portion of the REST API
"""
__author__ = 'rpcanno'

from base import JsonTests
from defaults import Default


class ComponentTests(JsonTests):
    def setUp(self):
        json, resp = self._json_request(
            '/domains/'+Default.DOMAIN_NAME+'/waveforms',
            200,
            'POST',
            {'name': Default.WAVEFORM}
        )
        self.assertTrue('launched' in json)
        self.base_url = '/domains/%s/waveforms/%s' % (Default.DOMAIN_NAME, json['launched'])

    def tearDown(self):
        self._json_request(
            self.base_url,
            200,
            'DELETE'
        )

    def _get_comps(self):
        json, resp = self._json_request(self.base_url, 200)
        self.assertTrue('components' in json)

        return json['components']

    def test_list(self):
        components = self._get_comps()

        json, resp = self._json_request(self.base_url + '/components', 200 )

        self.assertIdList(json, 'components')
        self.assertEquals(components, json['components'])

    def test_info(self):
        components = self._get_comps()

        comp_id = components[0]
        json, resp = self._json_request(self.base_url+"/components/"+comp_id, 200)

        self.assertList(json, 'ports')

        self.assertAttr(json, 'id', comp_id)
        self.assertAttr(json, 'name', Default.COMPONENT)

        self.assertList(json, 'properties')
        self.assertProperties(json['properties'])