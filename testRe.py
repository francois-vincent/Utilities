# -*- coding: utf-8 -*-

import re

def basic_re():
    pattern = r"(\d+)"
    cre = re.compile(pattern)
    print "groupindex", cre.groupindex
    print "pattern", cre.pattern

    string = "<123456-1212>"
    print "string", string

    findall = cre.findall(string)
    print "findall", findall
    match = cre.match(string)
    print "match", match
    search = cre.search(string)
    print "search", search
    print "  group", search.group()
    print "  groups", search.groups()
    print "  span", search.span()
    split = cre.split(string)
    print "split", split

def date_re():
    pattern = r"(\d+)/(\d+)/(\d+)"
    cre = re.compile(pattern)
    print "groupindex", cre.groupindex
    print "pattern", cre.pattern

    string = "birthday: 12/06/1964"
    print "string", string

    findall = cre.findall(string)
    print "findall", findall
    match = cre.match(string)
    print "match", match
    search = cre.search(string)
    print "search", search
    print "  group", search.group()
    print "  groups", search.groups()
    print "  span", search.span()
    split = cre.split(string)
    print "split", split

def kodos_re():
    pattern = r"(?P<key>.*?)=(?P<value>.*?)(?:\s|$)"
    cre = re.compile(pattern)
    print "groupindex", cre.groupindex
    print "pattern", cre.pattern

    string = "color=green color=white color=yellow"
    print "string", string

    findall = cre.findall(string)
    print "findall", findall
    match = cre.match(string)
    print "match", match
    if match:
        print "  group", match.group()
        print "  groups", match.groups()
    search = cre.search(string)
    print "search", search
    if search:
        print "  group", search.group()
        print "  groups", search.groups()
        print "  span", search.span()
    split = cre.split(string)
    print "split", split

#basic_re()
#date_re()
kodos_re()
