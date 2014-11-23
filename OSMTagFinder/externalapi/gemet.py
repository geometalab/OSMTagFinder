# -*- coding: utf-8 -*-
'''
Created on 01.11.2014

@author: Simon Gwerder
'''

from ordered_set import OrderedSet
from thesauribase import ThesauriBase
from utilities.configloader import ConfigLoader
from utilities import utils
from utilities.retry import retry

import requests


class Gemet(ThesauriBase):

    cl = ConfigLoader()
    uri = cl.getGemetAPIString('URI')
    getConceptByID = cl.getGemetAPIString('GET_CONCEPT_BY_ID')
    getRelatives = cl.getGemetAPIString('GET_RELATIVES')
    conceptSuffix = cl.getGemetAPIString('CONCEPT_SUFFIX')
    getConceptByKeyword = cl.getGemetAPIString('GET_CONCEPT_BY_KEYWORD')
    thesaaurusSuffix = cl.getGemetAPIString('THESAURUS_SUFFIX')
    searchModeSuffix = cl.getGemetAPIString('SEARCH_MODE_SUFFIX')
    langSuffix = cl.getGemetAPIString('LANGUAGE_SUFFIX')

    searchMode = 4 # from 0 to 4, 4 is automode

    relatedSet = OrderedSet()
    broaderSet = OrderedSet()
    narrowerSet = OrderedSet()


    def __init__(self, searchTerm, language):
        ThesauriBase.__init__(self, searchTerm, language)
        self.relatedSet = OrderedSet()
        self.broaderSet = OrderedSet()
        self.narrowerSet = OrderedSet()
        self.supportedLang.append('de')
        self.supportedLang.append('en')

        if language in self.supportedLang:
            for word in self.searchTerms:
                self.runAPICall(word, language)

    @retry(Exception, tries=3)
    def apiCall(self, word, apiLang):
        return requests.get(self.getConceptByKeyword + word + self.langSuffix + apiLang +
                            self.searchModeSuffix + str(self.searchMode) +
                            self.thesaaurusSuffix + self.uri)

    def runAPICall(self, word, apiLang):

        searchResult = self.apiCall(word, apiLang)

        if searchResult.status_code < 300:
            searchJson = searchResult.json()
            for category in searchJson:
                conceptUri = category['uri']
                thisPrefLabel = self.getConceptForUri(conceptUri, apiLang)
                if thisPrefLabel is not None:
                    self.relatedSet.append(utils.eszettToSS(thisPrefLabel))
                relativesResult = requests.get(self.getRelatives + self.conceptSuffix + conceptUri)
                if relativesResult.status_code < 300:
                    relativesJson = relativesResult.json()

                    for relation in relativesJson:
                        if 'related' in relation['relation']:
                            thisAltLabel = self.getConceptForUri(relation['target'], apiLang)
                            if thisAltLabel is not None:
                                self.relatedSet.append(utils.eszettToSS(thisAltLabel))
                        if 'narrower' in relation['relation']:
                            thisNarrowerLabel = self.getConceptForUri(relation['target'], apiLang)
                            if thisNarrowerLabel is not None:
                                self.narrowerSet.append(utils.eszettToSS(thisNarrowerLabel))
                        if 'broader' in relation['relation']:
                            thisBroaderLabel = self.getConceptForUri(relation['target'], apiLang)
                            if thisBroaderLabel is not None:
                                self.broaderSet.append(utils.eszettToSS(thisBroaderLabel))



    def getConceptForUri(self, gemetConceptUri, apiLang):
        try:
            conceptResult = requests.get(self.getConceptByID + self.conceptSuffix + gemetConceptUri + self.langSuffix + apiLang)
            if conceptResult.status_code < 300:
                conceptJson = conceptResult.json()
                if 'preferredLabel' in conceptJson:
                    return (conceptJson['preferredLabel'])['string']
        except:
            return None

    def getRelated(self):
        return self.relatedSet

    def getNarrower(self):
        return self.narrowerSet

    def getBroader(self):
        return self.broaderSet

    def checkConnection(self):
        response = self.apiCall('test', 'en')
        if response is not None and response.status_code < 300:
            return True
        return False


if __name__ == '__main__':
    g = Gemet('Geschäft', 'de')

    print "Related: "
    for related in g.getRelated():
        print related

    print "\nNarrower: "
    for narrower in g.getNarrower():
        print narrower

    print "\nBroader: "
    for broader in g.getBroader():
        print broader