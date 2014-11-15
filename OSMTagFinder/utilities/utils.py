# -*- coding: utf-8 -*-
'''
Created on 08.10.2014

@author: Simon Gwerder
'''

import re
import os
import datetime
import json


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
    path = rootDir() + '/' + _dataFolderName + '/'
    return _checkPath(path)

def indexerDir():
    path = dataDir() + '/' + _indexerFolderName + '/'
    return _checkPath(path)

def staticDir():
    path = rootDir() + '/' + _staticFolderName + '/'
    return _checkPath(path)

def templatesDir():
    path = rootDir() + '/' + _templatesFolderName + '/'
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
    return u'\xc3\x9f' in word

def hasSS(word):
    return 'ss' in word

def eszettToSS(word):
    if word is not None:
        return word.replace(u'\xc3\x9f', 'ss')

def ssToEszett(word):
    if word is not None:
        return word.replace('ss', u'\xc3\x9f')

_digits = re.compile('\d')
def containsDigits(d):
    return bool(_digits.search(d))

def outputFile(directory, outputName, outputExtension, useDateEnding):
    '''Returns full file path. If 'useDateEnding' is True, a date postfix is added between
       the filename and ending, of the form '_yymmdd'.'''
    if useDateEnding:
        dateString = datetime.date.today().isoformat()
        dateString = dateString.replace('-', '')
        dateString = dateString[2:]  # substring from incl. 3rd char to end of string
        return directory + '/' + outputName + '_' + dateString + outputExtension
    else:
        return directory + '/' + outputName + outputExtension

def fileLoader(baseDir, extension):
    '''Returns a list of files that are in the 'baseDir' directory or in a subdirectory
       of it. The fileending is 'extension' (e.g. 'rdf' or '.rdf').'''
    extension = extension.replace('.','') # in case someone calls this function with '.' ending
    foundFiles = []
    if extension is None: return None
    for root, dirs, files in os.walk(baseDir):
        for f in files:
            if f.endswith('.' + extension):
                foundFiles.append(os.path.join(root, f))
                dirs # just to get rid of the not-used warning
    return foundFiles


def getAsteriskSymbol():
    '''Returns asterisk '✱' symbol'''
    return '✱' # ✱✲

def genToList(generator):
    retList = []
    for item in generator:
        retList.append(item)
    return retList

def genToLangDict(generator):
    retDict = {}
    for item in generator:
        retDict[item.language] = item
    return retDict;

def genGetFirstItem(generator):
    try:
        firstItem = generator.next()
    except StopIteration:
        return None
    return str(firstItem)

def genJsonToDict(generator, default=None):
    jsonStr = genGetFirstItem(generator)
    try:
        return json.loads(str(jsonStr))
    except ValueError:
        return default



