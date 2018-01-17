# https://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
# TODO add unittests

from functools import wraps
from time import sleep


def retry_scalar(exceptions_retry=Exception, exceptions_abort=None, max_exec=3, delay=1, progress=1, logger=None):
    """ Retry decorator with a counter
    :param exceptions_retry: an exception or a tuple of exceptions to retry
    :param exceptions_abort: an exception or a tuple of exceptions to abort
    :param max_exec: max number of executions (= max number of retries + 1)
    :param delay: a sleep time between executions, in seconds
    :param progress: the delay is multiplied by or added to this parameter after each execution:
                     multiply if progress is positive, added with opposite if progress is negative
    :param logger: a logging.logger instance or None
    """
    def deco_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            _max_exec, = max_exec if max_exec > 1 else 1
            _delay = delay if delay > 0 else 0
            while _max_exec > 1:
                try:
                    return f(*args, **kwargs)
                except exceptions_abort as e:
                    if logger:
                        logger.error("%s Raised, aborting." % str(e))
                    raise
                except exceptions_retry as e:
                    if logger:
                        logger.warning("%s, Retrying in %d seconds..." % (str(e), _delay))
                    if _delay > 0:
                        sleep(_delay)
                        if progress > 0:
                            _delay *= progress
                        else:
                            _delay += -progress
                    _max_exec -= 1
            return f(*args, **kwargs)
        return f_retry
    return deco_retry


def retry_vector(exceptions_retry=Exception, exceptions_abort=None, delays=(1, 1, 1), logger=None):
    """ Retry decorator with a tuple of retry delays
    :param exceptions_retry: an exception or a tuple of exceptions to retry
    :param exceptions_abort: an exception or a tuple of exceptions to abort
    :param delays: a tuple of sleep time between executions, in seconds, such that max number of
           executions= len(delays) + 1
    :param logger: a logging.logger instance or None
    """
    def deco_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            _delays = delays
            while _delays:
                _delay = _delays[0]
                try:
                    return f(*args, **kwargs)
                except exceptions_abort as e:
                    if logger:
                        logger.error("%s Raised, aborting." % str(e))
                    raise
                except exceptions_retry as e:
                    if logger:
                        logger.warning("%s, Retrying in %d seconds..." % (str(e), _delay))
                    if _delay > 0:
                        sleep(_delay)
                    _delays = _delays[1:]
            return f(*args, **kwargs)
        return f_retry
    return deco_retry
