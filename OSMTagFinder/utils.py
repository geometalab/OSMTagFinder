# -*- coding: utf-8 -*-
'''
Created on 08.10.2014

@author: Simon Gwerder
'''

import re
import os

invalidChars = [' ', ';']
dataFolderName = 'data'
resourceFolderName = 'resource'

def rootDir():
    return os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]

def dataDir():
    return rootDir() + '/' + dataFolderName + '/'

def resourceDir():
    return rootDir() + '/' + resourceFolderName + '/'

def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def validCharsCheck(s):
    if containsDigits(s):
        return False

    for invalidChar in invalidChars:
        if invalidChar in s:
            return False

    return True

_digits = re.compile('\d')
def containsDigits(d):
    return bool(_digits.search(d))