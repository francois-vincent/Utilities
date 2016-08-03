#! /usr/bin/env python

#############################################
# Nagios probe that checks RabbitMQ
# queues that are not empty.
#
# On the target machine,
# you must edit sudoers with this command:
# visudo -f /etc/sudoers
# and add this line at the end of the file:
# nagios ALL = (root) NOPASSWD: /usr/sbin/rabbitmqctl
#############################################

from __future__ import print_function
import os.path
import subprocess

from clingon import clingon

debug = False
clingon.DEBUG = debug

NAGIOS_CRITICAL = 2
NAGIOS_WARNING = 1


class Persistence(object):
    def __init__(self, path='/var/lib/nagios/.rabbit_q.last'):
        self.path = path
        if not os.path.exists(path):
            with open(path, 'w') as f:
                f.write('')

    def read(self):
        with open(self.path, 'r') as f:
            return f.read()

    def write(self, data):
        with open(self.path, 'w') as f:
            f.write(data)


def print_message_exit(reported, truncate):
    reported = tuple(reported)
    more = False
    if truncate:
        more = len(reported) > truncate
        reported = reported[:truncate]
    print('RabbitMQ queues not empty: ' + ', '.join(reported) + (' (more)' if more else ''))
    exit(NAGIOS_WARNING)


@clingon.clize
def rabbit_queues(command='sudo /usr/sbin/rabbitmqctl list_queues',
                  prefix='kraken_mut-prd-',
                  limit=10,
                  truncate=5,
                  no_double=False):
    """
    Nagios probe that checks RabbitMQ queues that are not empty.
    Param 'command' allows to run another command, e.g. for debug.
    Param 'prefix' is a filter on queues names prefix.
    Param 'limit' is a filter on queues depth.
    Param 'truncate' will truncate the number of reported queues (if !=0).
    Param 'no_double' will toggle between single and double check.
    """
    try:
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        stdout, _ = p.communicate()
        if p.returncode != 0:
            print('Critical {} error: return code={}'.format(command, p.returncode))
            exit(NAGIOS_CRITICAL)
        queues = [q.split() for q in stdout.split('\n') if q.startswith(prefix)]
        queues = set(q.replace(prefix, '') for q, d in queues if int(d) >= limit)
        if not no_double:
            persist = Persistence()
            try:
                offenders = queues.intersection(persist.read().split('\n'))
                if offenders:
                    print_message_exit(offenders, truncate)
            finally:
                persist.write('\n'.join(queues))
        else:
            if queues:
                print_message_exit(queues, truncate)
    except Exception as e:
        if debug:
            raise
        print('Critical: {}'.format(e))
        exit(NAGIOS_CRITICAL)
    print("RabbitMQ queues OK")
    exit(0)
