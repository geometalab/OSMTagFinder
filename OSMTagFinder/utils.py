# -*- coding: utf-8 -*-
'''
Created on 08.10.2014

@author: Simon Gwerder
'''

import re
import os

_invalidChars = [' ', ';']
_dataFolderName = 'data'
_resourceFolderName = 'resource'

def rootDir():
    return os.path.split(os.path.abspath(os.path.dirname(__file__)))[0] + '\\' + os.path.split(os.path.abspath(os.path.dirname(__file__)))[1]

def dataDir():
    return rootDir() + '\\' + _dataFolderName + '\\'

def resourceDir():
    return rootDir() + '\\' + _resourceFolderName + '\\'

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

_digits = re.compile('\d')
def containsDigits(d):
    return bool(_digits.search(d))

