# encoding: utf-8
# from http://amoffat.github.io/sh/

from contextlib import contextmanager
import sh
from threading import Thread
import time

# ps aux | grep ssh | awk '{print $11}'
print(sh.awk(sh.grep(sh.ps('aux'), 'ssh'), '{print $11}'))

print(sh.grep(sh.docker.version(), 'Version:'))

# most recent file
print(sh.tail(sh.ls('-lrt'), '-n 1'))


@contextmanager
def parallel_delayed_run(callable, *args, **kwargs):
    delay = kwargs.get('delay', 0.5)
    def delayed_run():
        time.sleep(delay)
        callable(*args)
    th = Thread(target=delayed_run)
    th.start()
    try:
        yield
    except sh.SignalException:
        print('Interrupted !')
    th.join()

toto = sh.tail('-f', '/var/log/syslog', _bg=True)
print(dir(toto))
print(toto.pid)
print(toto._process_completed)
with parallel_delayed_run(toto.process.signal, 2):
    toto.wait()
