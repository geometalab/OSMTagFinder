# -*- coding: utf-8 -*-
'''
Created on 31.10.2014

@author: Simon Gwerder
'''

import abc
from abc import ABCMeta
from utilities import utils

class ThesauriBase(object):
    __metaclass__ = ABCMeta

    searchTerms = None
    supportedLang = None

    def __init__(self, searchTerm, language):
        self.searchTerms = []
        self.searchTerms.append(searchTerm)
        if utils.hasEszett(searchTerm):
            self.searchTerms.append(utils.eszettToSS(searchTerm))
        elif utils.hasSS(searchTerm):
            self.searchTerms.append(utils.ssToEszett(searchTerm))

        self.supportedLang = []

    def getSupportedLang(self):
        return self.supportedLang

    def getSearchTerms(self):
        return self.searchTerms

    @abc.abstractmethod
    def getRelated(self):
        '''Returns an ordered set containing all synonyms and other related terms for 'searchTerm'.'''
        return

    @abc.abstractmethod
    def getNarrower(self):
        '''Returns an ordered set containing all narrower terms for 'searchTerm'. this > result'''
        return

    @abc.abstractmethod
    def getBroader(self):
        '''Returns an ordered set containing all broader terms for 'searchTerm'. this < result'''
        return



