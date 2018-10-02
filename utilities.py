
import random
import re


try:
  basestring
except NameError:
  basestring = str

try:
  xrange
except NameError:
  xrange = range


def isstring(x):
    return isinstance(x, basestring)


UUID_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyz"
UUID_ALPHABET_WITH_UPPERCASE = UUID_ALPHABET + "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
NUMBER_CLEANER_RE = re.compile(r"\D+")


def make_id_with_prefix(prefix='', length=8, with_uppercase=False):
    """Make a new id by joining randomly picked chars from alphabet"""
    alphabet = UUID_ALPHABET_WITH_UPPERCASE if with_uppercase else UUID_ALPHABET
    rs = ''.join(random.choice(alphabet) for _ in xrange(length))
    return prefix + '_' + rs if prefix else rs


def clean_number(number):
    """
    Remove any non numeric char from number
    :param number: string
    :return: cleaned string
    """
    return NUMBER_CLEANER_RE.sub('', number)
