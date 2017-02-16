#! /usr/bin/env python

import argparse
from importlib import import_module
import json
import os
import os.path as osp
import falcon
from falcon import api_helpers as helpers

#
# API decorators and classes
#
def swagger(**swargs):
    def swagger_decorator(func):
        func.__swagger__ = swargs
        return func
    return swagger_decorator

def swaggerOptions(original_class):
    def on_options(self, req, resp, *args, **kwargs):
        resp.status = falcon.HTTP_200
        resp.set_header('Access-Control-Allow-Origin', "*")
        resp.set_header('Access-Control-Allow-Methods', "POST, GET, PUT, DELETE, OPTIONS")
        resp.set_header('Access-Control-Allow-Headers', "Content-Type, api_key, Authorization")

    original_class.on_options = on_options

    return original_class

class SwaggerResource(object):
    def on_options(self, req, resp, *args, **kwargs):
        resp.status = falcon.HTTP_200
        resp.set_header('Access-Control-Allow-Origin', "*")
        resp.set_header('Access-Control-Allow-Methods', "POST, GET, PUT, DELETE, OPTIONS")
        resp.set_header('Access-Control-Allow-Headers', "Content-Type, api_key, Authorization")

class SwaggerConfigResource(SwaggerResource):
    """
    Swagger config
    """
    def __init__(self, app):
        self.app = app
        self.swagger_def = None

    @swagger(summary="swagger description", response="the swagger config")
    def on_get(self, req, resp):
        if self.swagger_def == None:
            self.swagger_def = build_swagger_def(self.app)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(self.swagger_def)


class CorsMiddleware(object):
    def process_request(self, request, response):
        response.set_header('Access-Control-Allow-Origin', '*')

def swaggerify(app, name, version):
    assert(isinstance(app, falcon.api.API))

    falcon.API.__swagger__ = {'name': name, 'version': version }
    app._middleware += helpers.prepare_middleware([CorsMiddleware()])
    app.add_route('/swagger.json', SwaggerConfigResource(app))

#
# config generation script
#
def format_parameters(info, path, method_name):
    parameters = list()

    if 'parameters' in info:
        for pname, pinfo in info['parameters'].iteritems():
            pinfo['name'] = pname

            # guess the type
            if 'in' not in pinfo:
                if path.find('{%s}' % pname) >= 0:
                    pinfo['in'] = 'path'
                    pinfo['required'] = True
                else:
                    pinfo['in'] = 'query'
            parameters.append(pinfo)
        del info['parameters']

    # shorthand for body parameters
    if 'body' in info:
        body_info = {
            'name': 'payload',
            'in': 'body',
            'schema': {
                "type": "object",
                "required": [],
                "properties": {}
            }
        }

        for pname, pinfo in info['body'].iteritems():
            if 'required' in pinfo:
                body_info['schema']['required'].append(pname)
                del pinfo['required']

            body_info['schema']['properties'][pname] = pinfo

        parameters.append(body_info)
        del info['body']

    info['parameters'] = parameters

def format_response(info, method_name):

    # shorthand for standard 200 response
    if 'response' in info:
        responses = dict()
        responses['200'] = info['response']
        del info['response']
        info['responses'] = responses

    if 'responses' not in info:
        raise Exception('Missing required response info for %s' % method_name)

def build_method_info(resource, path, method):
    method_name = '%s.on_%s()' % (resource.__name__, method)

    try:
        info = getattr(resource, 'on_%s' % method).__swagger__
    except:
        raise Exception('missing swagger decorator for %s' % method_name)

    format_parameters(info, path, method_name)
    format_response(info, method_name)

    return info

def build_resource_info(resource, path):
    info = dict()

    for method in ['get', 'post', 'put', 'delete']:
        if hasattr(resource, 'on_%s' % method):
            info[method] = build_method_info(resource, path, method)

    return info

def build_resource_list(nodes, path=''):
    resource_list = list()
    for node in nodes:
        node_path = "%s/%s" % (path, node.raw_segment)
        if node.resource:
            resource_list.append((node_path, node.resource.__class__))
        resource_list.extend(build_resource_list(node.children, node_path))

    return resource_list

def build_swagger_def(app):
    assert(isinstance(app, falcon.api.API))

    resources = build_resource_list(app._router._roots)
    resources_info = dict([(path, build_resource_info(resource, path)) for path, resource in resources])

    info = app.__swagger__

    return {
        'swagger': '2.0',
        'info': info,
        'produces': [app._media_type],
        'paths': resources_info
    }

def build_swagger_def_for_api(falcon_api):
    falcon_api_module, falcon_api_app = falcon_api.split(':')
    app = getattr(import_module(falcon_api_module), falcon_api_app)

    return build_swagger_def(app)

def main():
    parser = argparse.ArgumentParser(description='Build user targeting')
    parser.add_argument('falcon_api', help='The falcon api')
    args = parser.parse_args()

    swagger_def = build_swagger_def_for_api(args.falcon_api)

    print json.dumps(swagger_def, indent=4)

if __name__=="__main__":
    main()
