# Copyright 2017 Kosc Telecom

import socket


def valid_ipv4(address):
    if not address:
        return False
    try:
        socket.inet_aton(address)
        return True
    except:
        return False
