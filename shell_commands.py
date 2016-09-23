# encoding: utf-8

import cStringIO
from subprocess import Popen, PIPE, call
import sys
import threading


COMMAND_DEBUG = None
# COMMAND_DEBUG = 'Debug: '


class Command(object):
    """ Use this class if you want to wait and get shell command output
    """
    def __init__(self, cmd, show=COMMAND_DEBUG):
        self.show = show
        self.p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        self.out_buf = cStringIO.StringIO()
        self.err_buff = cStringIO.StringIO()
        t_out = threading.Thread(target=self.out_handler)
        t_err = threading.Thread(target=self.err_handler)
        t_out.start()
        t_err.start()
        self.p.wait()
        t_out.join()
        t_err.join()
        self.p.stdout.close()
        self.p.stderr.close()
        self.stdout = self.out_buf.getvalue()
        self.stderr = self.err_buff.getvalue()
        self.returncode = self.p.returncode

    def out_handler(self):
        for line in iter(self.p.stdout.readline, ''):
            if self.show is not None:
                sys.stdout.write(self.show + line)
            self.out_buf.write(line)

    def err_handler(self):
        for line in iter(self.p.stderr.readline, ''):
            if self.show is not None:
                sys.stderr.write(self.show + 'Error: ' + line)
            self.err_buff.write(line)


def command(cmd, raises=False):
    """ Use this function if you only want the return code.
        You can't retrieve stdout nor stderr and it never raises
    """
    ret = call(cmd, shell=True)
    if ret and raises:
        raise RuntimeError("Error while executing <{}>".format(cmd))
    return ret


def command_input(cmd, datain, raises=False):
    """ Use this if you want to send data to stdin
    """
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    p.communicate(datain)
    if p.returncode and raises:
        raise RuntimeError("Error while executing <{}>".format(cmd))
    return p.returncode
