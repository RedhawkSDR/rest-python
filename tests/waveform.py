"""
Tornado tests for the /domain/{NAME}/waveforms portion of the REST API
"""
__author__ = 'rpcanno'

from base import JsonTests
from defaults import Default


class WaveformTests(JsonTests):
    def _get_waveforms(self):
        url = '/domains/'+Default.DOMAIN_NAME
        json, resp = self._json_request(url, 200)

        self.assertTrue('waveforms' in json)

        return url, json['waveforms']

    def _launch(self, name):
        json, resp = self._json_request(
            '/domains/'+Default.DOMAIN_NAME+'/waveforms',
            200,
            'POST',
            {'name': name}
        )
        self.assertTrue('launched' in json)
        self.assertTrue('waveforms' in json)
        self.assertTrue(json['launched'] in [x['id'] for x in json['waveforms']])

        return json['launched']

    def _release(self, wf_id):
        json, resp = self._json_request(
            '/domains/'+Default.DOMAIN_NAME+'/waveforms/'+wf_id,
            200,
            'DELETE'
        )

        self.assertTrue('released' in json)
        self.assertEquals(json['released'], wf_id)

        self.assertTrue('waveforms' in json)
        self.assertFalse(json['released'] in json['waveforms'])

    def test_launch_release(self):
        url, waveforms = self._get_waveforms()
        json, resp = self._json_request(url+'/waveforms', 200)

        self.assertTrue('available' in json)
        self.assertTrue(Default.WAVEFORM in [x['name'] for x in json['available']])

        wf_id = self._launch(Default.WAVEFORM)
        self._release(wf_id)

    def test_list(self):
        url, waveforms = self._get_waveforms()
        json, resp = self._json_request(url+'/waveforms', 200)

        self.assertTrue('available' in json)
        self.assertTrue(isinstance(json['available'], list))
        for app in json['available']:
            self.assertTrue('sad' in app)
            self.assertTrue('name' in app)

        self.assertTrue('waveforms' in json)
        self.assertTrue(isinstance(json['waveforms'], list))

        for wf in json['waveforms']:
            self.assertTrue('id' in wf)
            self.assertTrue('name' in wf)

        self.assertEquals(waveforms, json['waveforms'])