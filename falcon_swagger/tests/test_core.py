""" Unit tests for falcon swagger """
import unittest
import json
from collections import OrderedDict

from falcon import API

from falcon_swagger.core import build_swagger_def
from falcon_swagger.core import swagger
from falcon_swagger.core import swaggerify


class TargetingControlStoreUnittests(unittest.TestCase):
    """ Unit tests for the Targeting Control store.
    """

    def test_build_swagger_def_1(self):
        class TestResource(object):
            @swagger(summary='Get active campaign',
                     responses={'200': {'description': 'Get succeed'},
                                '404': {'description': 'Impossible to retrieve the '
                                        'active campaign'}},
                     tags=['campaign'])
            def on_get(self, req, resp):
                """ Get active campaign in the store.
                """
                try:
                    self.format_success(resp=resp,
                                        content=self.store.get_active_campaign())
                except:
                    self.format_error(resp=resp, error_msg=format_exc())

        app = API()
        swaggerify(app, 'test-api', '2.0.0', host="localhost")
        app.add_route('/test/active-campaign', TestResource())

        expected = {
            'info': {'version': '2.0.0', 'name': 'test-api', 'host': 'localhost'},
            'paths': OrderedDict({
                '/test/active-campaign': {
                    'get': {
                        'tags': ['campaign'],
                        'responses': {
                            '200': {'description': 'Get succeed'},
                            '404': {'description': 'Impossible to retrieve the active campaign'}
                        },
                        'parameters': [],
                        'summary': 'Get active campaign'}
                }
            }),
            'swagger': '2.0',
            'produces': [app._media_type]
        }
        swagger_def = build_swagger_def(app)
        self.maxDiff = None
        self.assertEquals(expected, swagger_def)

    def test_build_swagger_def_2(self):
        class TestResource(object):
            @swagger(summary='test')
            def on_get(self, req, resp):
                pass

        app = API()
        swaggerify(app, 'test-api', '2.0.0', host="localhost")
        app.add_route('/test/', TestResource())
        app.add_route('/test/list/item', TestResource())
        app.add_route('/test/list', TestResource())
        app.add_route('/pipo', TestResource())
        app.add_route('/bla', TestResource())

        expected = [
            '/bla',
            '/pipo',
            '/test',
            '/test/list',
            '/test/list/item'
            ]
        swagger_def = build_swagger_def(app)
        self.maxDiff = None
        self.assertEquals(expected, swagger_def['paths'].keys())
