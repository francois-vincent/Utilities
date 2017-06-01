#! /usr/bin/env python

from clingon import clingon
try:
    import simplejson as json
except ImportError:
    import json
import os.path
import requests

# clingon.DEBUG = True

default_headers = {}


def get_request(verb):
    return getattr(requests, verb)


def pformat(pyobj):
    return json.dumps(pyobj, indent=4)


@clingon.clize
def run(service,
        verb='GET',
        data='',
        file_data='',
        target='http://localhost:8080',
        output='',
        headers='',
        show_headers=False,
        debug=False,
        xml2json=False):
    """
    Launch an HTTP request with optional POST/PUT data
    URL = host + service
    Service can be specified with parameter, i.e. 'operators/:id'
    Output can be specified with encoding, i.e. 'response.txt:latin (defaults to utf8)
    """
    verb = verb.lower()
    url = target.rstrip('/') + '/' + service.strip('/') + '/'
    kwargs = dict(headers=dict(default_headers, **eval(headers)) if headers else default_headers, verify=False)
    if file_data:
        with open(os.path.expanduser(file_data), 'rb') as f:
            data = f.read()
    if data:
        kwargs['data'] = eval(data)
    if debug:
        print("Request Headers")
        print(pformat(kwargs))
    r = get_request(verb)(url, **kwargs)
    print("{} {} - {}".format(verb.upper(), r.url, r.status_code))
    if show_headers:
        print("Response Headers")
        print(pformat(dict(r.headers)))
        print("Data")
    try:
        out = pformat(r.json())
    except ValueError:
        out = r.text
        if xml2json:
            import xmltodict
            out = pformat(xmltodict.parse(out))
    print(out)
    if output:
        output, encoding = output.split(':') if ':' in output else (output, 'utf8')
        with open(output, 'wb') as f:
            f.write(out.encode(encoding))
