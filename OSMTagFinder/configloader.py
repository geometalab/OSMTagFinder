# -*- coding: utf-8 -*-
'''
Created on 10.10.2014

@author: Simon Gwerder
'''

from ConfigParser import SafeConfigParser
import codecs
import utils

class ConfigLoader:

    configFileLoc = utils.dataDir() + 'config.ini'

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