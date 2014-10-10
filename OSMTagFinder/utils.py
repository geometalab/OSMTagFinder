# -*- coding: utf-8 -*-
'''
Created on 08.10.2014

@author: Simon Gwerder
'''

import re
import os
from ConfigParser import SafeConfigParser
import codecs

class Utils:
    invalidChars = [' ', ';']
    dataFolderName = 'data'
    resourceFolderName = 'resource'

    def rootDir(self):
        return os.path.split(os.path.abspath(os.path.dirname(__file__)))[0] + '\\' + os.path.split(os.path.abspath(os.path.dirname(__file__)))[1]

    def dataDir(self):
        return self.rootDir() + '\\' + self.dataFolderName + '\\'

    def resourceDir(self):
        return self.rootDir() + '\\' + self.resourceFolderName + '\\'

    def isNumber(self, r):
        try:
            float(r)
            return True
        except ValueError:
            return False

    def validCharsCheck(self, r):
        if self.containsDigits(r):
            return False

        for invalidChar in self.invalidChars:
            if invalidChar in r:
                return False

        return True

    _digits = re.compile('\d')
    def containsDigits(self, d):
        return bool(self._digits.search(d))




class ConfigLoader:

    configFileLoc = Utils().dataDir() + 'config.ini'

    thesaurusSection = 'Thesaurus'
    tagInfoSection = "TagInfoAPI"

    __parser = SafeConfigParser()

    def __init__(self):
        with codecs.open(self.configFileLoc, 'r', encoding='utf-8') as configFile:  # open the file with the correct encoding
            self.__parser.readfp(configFile)

    def getThesaurusString(self, option):
        return self.__parser.get(self.thesaurusSection, option)

    def getThesaurusInt(self, option):
        return self.__parser.getint(self.thesaurusSection, option)

    def getTagInfoAPIString(self, option):
        return self.__parser.get(self.tagInfoSection, option)








