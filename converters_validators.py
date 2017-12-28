# Copyright 2017 Kosc Telecom

import re
import socket

PRINTABLE_CHARS = re.compile(r'[^\x20-\x7e]*')


def clean_printables(data):
    return re.sub(PRINTABLE_CHARS, '', data) if data else None


def convert_camelcase(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def valid_ipv4(address):
    if not address:
        return False
    try:
        socket.inet_aton(address)
        return True
    except:
        return False
