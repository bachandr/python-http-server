#!/usr/bin/env python
"""
HTTP server with key value store in python

Usage::
    python3 ./http-server.py [<port>]

Send a GET request to retrieve all key value:
    curl -v -XGET http://localhost:{port}/store/key

Send a GET request to retrieve value for given key:
    curl -v -XGET http://localhost:{port}/store/key/{key}

Send a DELETE request to delete all key value:
    curl -v -XDELETE http://localhost:{port}/store/key

Send a DELETE request to delete entry for given key:
    curl -v -XDELETE http://localhost:{port}/store/key/{key}

Send a POST/PUT request to store key value:
    curl -v -XPOST "http://localhost:{port}/store/key/key}/value/{value}" -d '{}'
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
from enum import Enum
import json
import logging
import re

key_value_store = {}


class ResourceNotFoundError(Exception):
    """ Base class for resource not found exception. """

    def __init__(self, m):
        self.message = m

    def __str__(self):
        return self.message


class KeyNotFoundError(Exception):
    """ Base class for key not found exception. """

    def __init__(self, m):
        self.message = m

    def __str__(self):
        return self.message


class Action(Enum):
    GET = 1
    DELETE = 2


class Handler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, ctype='text/plain'):
        self.send_response(status)
        self.send_header('Content-type', ctype)
        self.end_headers()

    def _validate_path(self):
        if 'store' not in self.path:
            raise ResourceNotFoundError('Resource Not Found: %s' % self.path)

    def _to_json(self, status, data):
        self._set_headers(status, 'application/json')
        json_string = json.dumps(data)
        self.wfile.write(json_string.encode('UTF-8'))

    def _to_text(self, status, data):
        self._set_headers(status)
        self.wfile.write(data)

    @staticmethod
    def _get(key):
        try:
            return key_value_store.__getitem__(key)
        except KeyError as e:
            raise KeyNotFoundError('Key ' + key + ' not found')

    @staticmethod
    def _clear(key=None):
        if key is None:
            key_value_store.clear()
        else:
            try:
                key_value_store.pop(key)
            except KeyError as e:
                raise KeyNotFoundError('Key ' + key + ' not found')

    def _helper(self, action):
        self._validate_path()
        if not isinstance(action, Action):
            raise TypeError(action + ' must be an instance of Action Enum')
        try:
            if self.path.endswith("/key"):
                temp_store = {}
                temp_store.update(key_value_store)
                if action == Action.DELETE:
                    self._clear()
                return self._to_json(200, temp_store)
            elif bool(re.search("/key/(\\w+)", self.path)):
                match = re.search("/key/(\\w+)", self.path)
                key = match.group(1)
                value = self._get(key)
                if action == Action.DELETE:
                    self._clear(key)
                return self._to_json(200, {key: value})
            else:
                raise ResourceNotFoundError('Path not found ' + self.path)
        except ResourceNotFoundError as e:
            return self._to_json(404, {'error': e.message})
        except Exception as e:
            return self._to_json(500, {'error': e.message})

    def do_GET(self):
        self._helper(Action.GET)

    def do_DELETE(self):
        self._helper(Action.DELETE)

    def do_PUT(self):
        self.do_POST()

    def do_POST(self):
        self._validate_path()
        try:
            match = re.search("/key/(\\w+)/value/(\\w+)", self.path)
            if bool(match):
                key = match.group(1)
                value = match.group(2)
                key_value_store.update({key: value})
                return self._to_json(200, {key: value})
            else:
                raise ResourceNotFoundError('Path not found ' + self.path)
        except ResourceNotFoundError as e:
            return self._to_json(404, {'error': e.message})
        except Exception as e:
            return self._to_json(500, {'error': e.message})


def run(server_class=HTTPServer, handler_class=Handler, port=1090):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...')
    httpd.serve_forever()


if __name__ == "__main__":
    from sys import argv

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(threadName)s - %(name)s - %(message)s')
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
