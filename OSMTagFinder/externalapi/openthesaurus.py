# -*- coding: utf-8 -*-
'''
Created on 31.10.2014

@author: Simon Gwerder
'''

import requests
from ordered_set import OrderedSet
import xml.etree.ElementTree as ET

from thesauribase import ThesauriBase
from utilities.configloader import ConfigLoader
from utilities import utils

class OpenThesaurus(ThesauriBase):

    cl = ConfigLoader()

    synonymSet = OrderedSet()
    broaderSet = OrderedSet()
    narrowerSet = OrderedSet()

    def __init__(self, searchTerm):
        ThesauriBase.__init__(self, searchTerm)
        self.supportedLang.append('de')

        apiPrefix = self.cl.getOpenThesaurusAPIString('API_CALL')
        apiSuffix = self.cl.getOpenThesaurusAPIString('API_CALL_SUFFIX')

        for word in self.searchTerms:
            result = requests.get(apiPrefix + word + apiSuffix)
            xmlString = result.text
            self.parseXML(xmlString)
            if len(self.synonymSet) > 0:
                break

    def parseXML(self, xmlString):
        root = ET.fromstring(xmlString)

        for levelOne in root:
            if levelOne.tag == 'synset':
                synsetOne = levelOne
                for levelTwo in synsetOne:
                    if levelTwo.tag == 'term':
                        synonym = levelTwo.attrib['term']
                        self.synonymSet.append(utils.eszettToSS(synonym))
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

    def getSynonym(self):
        return self.synonymSet

    def getNarrower(self):
        return self.narrowerSet

    def getBroader(self):
        return self.broaderSet

if __name__ == '__main__':
    ot = OpenThesaurus('Fussball')

    print "Synonym: "
    for synonym in ot.getSynonym():
        print synonym

    print "\nNarrower: "
    for narrower in ot.getNarrower():
        print narrower

    print "\nBroader: "
    for broader in ot.getBroader():
        print broader



