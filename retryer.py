# https://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/

from functools import wraps
from time import sleep


def retry(exceptions_retry=Exception, exceptions_abort=None, nb_retry=3, delay=1, multiplier=1, logger=None):
    """ Retry decorator
    :param exceptions_retry: an exception or a tuple of exceptions to retry
    :param exceptions_abort: an exception or a tuple of exceptions to abort
    :param nb_retry: Nb of retries
    :param delay: a sleep time between retries in seconds
    :param multiplier: the delay is multiplied by this parameter after each retry
    :param logger: a logging.logger instance or None
    """
    def deco_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            _nb_retry, _delay = nb_retry, delay
            while _nb_retry > 1:
                try:
                    return f(*args, **kwargs)
                except exceptions_abort as e:
                    if logger:
                        logger.error("%s Raised, aborting." % (str(e), _delay))
                    raise
                except exceptions_retry as e:
                    if logger:
                        logger.warning("%s, Retrying in %d seconds..." % (str(e), _delay))
                    if _delay > 0:
                        sleep(_delay)
                        _delay *= multiplier
                    _nb_retry -= 1
            return f(*args, **kwargs)
        return f_retry
    return deco_retry
