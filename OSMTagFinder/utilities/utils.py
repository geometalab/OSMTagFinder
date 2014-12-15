# -*- coding: utf-8 -*-
'''
Created on 08.10.2014

@author: Simon Gwerder
'''

import re
import os
import datetime
import json
#import chardet


_invalidChars = [' ', ';']
_dataFolderName = 'data'
_indexerFolderName = 'indexer'
_websiteFolderName = 'web'
_staticFolderName = 'static'
_templatesFolderName = 'templates'
_tempFolderName = 'temp'
_semnetFolderName = 'semnet'
_testFolderName = 'test'

indexName = 'index'  # for indexer.py and graphsearch.py

def specCharEnc(text):
    text = encode(text)
    text = text.replace('Ä', '\xc3\x84')
    text = text.replace('ä', '\xc3\xa4')
    text = text.replace('Ö', '\xc3\x96')
    text = text.replace('ö', '\xc3\xb6')
    text = text.replace('Ü', '\xc3\x9c')
    text = text.replace('ü', '\xc3\xbc')
    text = text.replace('ß', '\xc3\x9f')
    return encode(text)

def encode(text):
    if text is not None and not isinstance(text, unicode) and len(text) > 0:
        #encoding = chardet.detect(text)
        try:
            return str( text.decode(encoding='UTF-8') ) #encoding['encoding']
        except:
            pass
    return text

def wsWord(word):
    word = word.replace('"', ' ')
    word = word.replace('_', ' ')
    word = word.replace(',', ' ')
    word = word.replace(';', ' ')
    word = word.replace(' = ', '=')
    word = eszettToSS(word)
    return word

def checkFile(filePath):
    return os.path.isfile(filePath)

def _checkCreatePath(path):
    if not os.path.exists(path):
        os.mkdir(path)
    return path

def rootDir():
    return os.path.split(os.path.abspath(os.path.dirname(__file__)))[0] # + '\\' + os.path.split(os.path.abspath(os.path.dirname(__file__)))[1]

def dataDir():
    path = rootDir() + '/' + _dataFolderName + '/'
    return _checkCreatePath(path)

def tempDir():
    path = rootDir() + '/' + _dataFolderName + '/' + _tempFolderName + '/'
    return _checkCreatePath(path)

def websiteDir():
    path = rootDir() + '/' + _websiteFolderName + '/'
    return _checkCreatePath(path)

def semnetDir():
    path = rootDir() + '/' + _dataFolderName + '/' + _semnetFolderName + '/'
    return _checkCreatePath(path)

def indexerDir():
    path = dataDir() + '/' + _indexerFolderName + '/'
    return _checkCreatePath(path)

def testDir():
    path = dataDir() + '/' + _testFolderName + '/'
    return _checkCreatePath(path)

def staticDir():
    path = websiteDir() + '/' + _staticFolderName + '/'
    return _checkCreatePath(path)

def templatesDir():
    path = websiteDir() + '/' + _templatesFolderName + '/'
    return _checkCreatePath(path)

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
    word = encode(word)
    return encode('ß') in word

def hasSS(word):
    return 'ss' in word

def eszettToSS(word):
    if word is not None:
        word = encode(word)
        return word.replace(encode('ß'), 'ss') # \xc3\x9f

def ssToEszett(word):
    if word is not None:
        word = encode(word)
        return encode(word.replace('ss', encode('ß'))) # \xc3\x9f

_digits = re.compile('\d')
def containsDigits(d):
    '''Returns true, if string 'd' contains a digit.'''
    return bool(_digits.search(d))

def uniquifyList(items):
    '''Removes duplicate elements in list 'items', while keeping order intact.'''
    seen = set()
    for i in xrange(len(items)-1, -1, -1):
        it = items[i]
        if it in seen:
            del items[i]
        else:
            seen.add(it)
    return items

def outputFile(directory, outputName, outputExtension, useDateEnding):
    '''Returns full file path. If 'useDateEnding' is True, a date postfix is added between
       the filename and ending, of the form '_yymmdd'.'''
    if useDateEnding:
        dateString = datetime.date.today().isoformat()
        dateString = dateString.replace('-', '')
        dateString = dateString[2:]  # substring from incl. 3rd char to end of string
        return directory + outputName + '_' + dateString + outputExtension
    else:
        return directory + outputName + outputExtension

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
    return encode(firstItem)

def genJsonToDict(generator, default=None):
    jsonStr = genGetFirstItem(generator)
    try:
        jsonData = json.loads(str(jsonStr))
        retDict = { }
        for key in jsonData:
            value = jsonData[key]
            if isNumber(value):
                retDict[key] = int(value)
            elif value == 'False':
                retDict[key] = False
            elif value == 'True':
                retDict[key] = True
            else:
                retDict[key] = value
        return retDict
    except ValueError:
        return default



