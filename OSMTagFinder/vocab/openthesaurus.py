# -*- coding: utf-8 -*-
'''
Created on 31.10.2014

@author: Simon Gwerder
'''

import requests
from ordered_set import OrderedSet
import xml.etree.ElementTree as ET

from vocabularybase import VocabularyBase
from utilities.configloader import ConfigLoader
from utilities import utils
from utilities.retry import retry

class OpenThesaurus(VocabularyBase):

    cl = ConfigLoader()
    apiPrefix = cl.getOpenThesaurusAPIString('API_URL')
    apiSuffix = cl.getOpenThesaurusAPIString('API_URL_SUFFIX')

    relatedSet = OrderedSet()
    broaderSet = OrderedSet()
    narrowerSet = OrderedSet()

    def __init__(self, searchTerm, language):
        VocabularyBase.__init__(self, searchTerm, language)
        self.relatedSet = OrderedSet()
        self.broaderSet = OrderedSet()
        self.narrowerSet = OrderedSet()
        self.supportedLang.append('de')

        if language in self.supportedLang:
            for word in self.searchTerms:
                result = self.apiCall(word, language)
                if result.status_code < 300:
                    xmlString = result.text
                    self.parseXML(xmlString)
                    if len(self.relatedSet) > 0:
                        break

    @retry(Exception, tries=3)
    def apiCall(self, word, apiLang):
        return requests.get(self.apiPrefix + word + self.apiSuffix)

    def parseXML(self, xmlString):
        root = ET.fromstring(xmlString)

        for levelOne in root:
            if levelOne.tag == 'synset':
                synsetOne = levelOne
                for levelTwo in synsetOne:
                    if levelTwo.tag == 'term':
                        synonym = levelTwo.attrib['term']
                        self.relatedSet.append(utils.eszettToSS(synonym))
                    elif levelTwo.tag == 'supersynsets':
                        for levelThree in levelTwo:
                            if levelThree.tag == 'synset':
                                for levelFour in levelThree:
                                    if levelFour.tag == 'term':
                                        broader = levelFour.attrib['term']
                                        self.broaderSet.append(utils.eszettToSS(broader))
                    elif levelTwo.tag == 'subsynsets':
                        for levelThree in levelTwo:
                            if levelThree.tag == 'synset':
                                for levelFour in levelThree:
                                    if levelFour.tag == 'term':
                                        narrower = levelFour.attrib['term']
                                        self.narrowerSet.append(utils.eszettToSS(narrower))

    def getRelated(self):
        return self.relatedSet

    def getNarrower(self):
        return self.narrowerSet

    def getBroader(self):
        return self.broaderSet

    def checkConnection(self):
        response = self.apiCall('test', 'de')
        if response is not None and response.status_code < 300:
            return True
        return False

if __name__ == '__main__':
    ot = OpenThesaurus('Coiffeur', 'de')

    print "Related: "
    for related in ot.getRelated():
        print related

    print "\nNarrower: "
    for narrower in ot.getNarrower():
        print narrower

    print "\nBroader: "
    for broader in ot.getBroader():
        print broader



