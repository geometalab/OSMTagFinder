# -*- coding: utf-8 -*-
'''
Created on 08.10.2014

@author: Simon Gwerder
'''

import re
import os
from collections import defaultdict

_invalidChars = [' ', ';']
_dataFolderName = 'data'
_indexerFolderName = 'indexer'
_staticFolderName = 'static'
_templatesFolderName = 'templates'

indexName = 'index'  # for indexer and graphsearch


def _checkPath(path):
    if not os.path.exists(path):
        os.mkdir(path)
    return path

def rootDir():
    return os.path.split(os.path.abspath(os.path.dirname(__file__)))[0] # + '\\' + os.path.split(os.path.abspath(os.path.dirname(__file__)))[1]

def dataDir():
    path = rootDir() + '\\' + _dataFolderName + '\\'
    return _checkPath(path)

def indexerDir():
    path = dataDir() + '\\' + _indexerFolderName + '\\'
    return _checkPath(path)

def staticDir():
    path = rootDir() + '\\' + _staticFolderName + '\\'
    return _checkPath(path)

def templatesDir():
    path = rootDir() + '\\' + _templatesFolderName + '\\'
    return _checkPath(path)

def isNumber(r):
    try:
        float(r)
        return True
    except ValueError:
        return False

def validCharsCheck(r):
    if containsDigits(r):
        return False

    for invalidChar in _invalidChars:
        if invalidChar in r:
            return False

    return True

def hasEszett(word):
    return 'ß' in word

def hasSS(word):
    return 'ss' in word

def eszettToSS(word):
    return word.replace('ß', 'ss')

def ssToEszett(word):
    return word.replace('ss', 'ß')

_digits = re.compile('\d')
def containsDigits(d):
    return bool(_digits.search(d))

def etreeToDict(t):
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etreeToDict, children):
            for k, v in dc.iteritems():
                dd[k].append(v)
        d = {t.tag: {k:v[0] if len(v) == 1 else v for k, v in dd.iteritems()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v) for k, v in t.attrib.iteritems())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
                d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d






