# coding: utf8

from __future__ import unicode_literals

CHAR_TRANSLATOR = {
    ord('-'): ' ',
    ord('_'): ' ',
    ord('.'): ' ',
    ord('à'): 'a',
    ord('â'): 'a',
    ord('æ'): 'ae',
    ord('é'): 'e',
    ord('è'): 'e',
    ord('ê'): 'e',
    ord('ë'): 'e',
    ord('î'): 'i',
    ord('ï'): 'i',
    ord('ô'): 'o',
    ord('œ'): 'oe',
    ord('ü'): 'u',
    ord('ç'): 'c',
    ord('À'): 'A',
    ord('Â'): 'A',
    ord('Æ'): 'AE',
    ord('É'): 'E',
    ord('È'): 'E',
    ord('Ê'): 'E',
    ord('Ë'): 'E',
    ord('Î'): 'I',
    ord('Ï'): 'I',
    ord('Ô'): 'O',
    ord('Ö'): 'O',
    ord('Œ'): 'OE',
    ord('Ü'): 'U',
    ord('Û'): 'U',
    ord('Ç'): 'C',
    ord(','): None,
    ord(';'): None,
    ord('*'): None,
    ord(':'): None,
    ord('!'): None,
    ord('?'): None,
    ord('#'): None,
    ord('+'): None,
    ord('\''): None,
    ord('"'): None,
    ord('\\'): None,
    ord('/'): None,
}


if __name__ == '__main__':
    print("Aix-en-Provence".translate(CHAR_TRANSLATOR))
    print("#François.Huré".translate(CHAR_TRANSLATOR))
    print("Gœthe Mælstrom".translate(CHAR_TRANSLATOR))
