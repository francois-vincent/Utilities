# coding: utf-8

from functools import partial

from clingon import clingon

# clingon.DEBUG = True

def test_blessings():
    from blessings import Terminal
    term = Terminal()
    print("This is %s and this is %s" % (term.green('green'), term.red('red')))


def test_termcolor():
    from termcolor import colored
    print("This is %s and this is %s" % (colored('green', 'green'), colored('red', 'red')))
    print("This is %s and this is %s" % (colored('green', 'green', 'on_yellow'), colored('red', 'red', 'on_yellow')))


def test_colored():
    from colored import fg, bg, attr
    class CO(object):
        def __init__(self, default_bg=0):
            self.default_bg = bg(default_bg)
        def format(self, color, string):
            return "%s%s%s" % (color, string, attr(0))
        def __getattr__(self, color):
            try:
                bg_color, fg_color = color.split('__')
                return partial(self.format, bg(bg_color) + fg(fg_color))
            except ValueError:
                return partial(self.format, self.default_bg + fg(color))
    co = CO()
    print("This is %s and this is %s" % (co.green('green'), co.red('red')))
    print("This is %s and this is %s" % (co.aquamarine_3('aquamarine_3'), co.medium_violet_red('medium_violet_red')))
    print("This is %s and this is %s" % (co.sandy_brown__aquamarine_3('aquamarine_3'), co.sandy_brown__medium_violet_red('medium_violet_red')))
    co = CO('grey_50')
    print("This is %s and this is %s" % (co.green('green'), co.red('red')))
    print("This is %s and this is %s" % (co.aquamarine_3('aquamarine_3'), co.medium_violet_red('medium_violet_red')))


@clingon.clize
def runner(blessings=False, termcolor=False, colored=False):
    if blessings:
        test_blessings()
    elif termcolor:
        test_termcolor()
    elif colored:
        test_colored()
    else:
        print("Please choose one of the available options")
