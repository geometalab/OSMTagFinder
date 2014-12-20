# -*- coding: utf-8 -*-
'''
Created on 01.11.2014

@author: Simon Gwerder
'''

from vocabularybase import VocabularyBase
from utilities.configloader import ConfigLoader
from utilities import utils
from utilities.retry import retry

from ordered_set import OrderedSet
import requests

class Altervista(VocabularyBase):

    apiKeys = ['WLNmjWebV5RMaqVjDk8b', 'QGqbbwnP9lRMW35ZwJcV', 'RTRtk7E5eB3WYg9NWwEE'] # 5000 queries a day per key

    splitChar = '|'

    cl = ConfigLoader()
    apiStr = cl.getAltervistaAPIString('API_CALL')
    keySuffix = cl.getAltervistaAPIString('KEY_SUFFIX')
    langSuffix = cl.getAltervistaAPIString('LANGUAGE_SUFFIX')

    relatedSet = OrderedSet()
    broaderSet = OrderedSet()
    narrowerSet = OrderedSet()

    def __init__(self, searchTerm, language):
        VocabularyBase.__init__(self, searchTerm, language)
        self.relatedSet = OrderedSet()
        self.broaderSet = OrderedSet()
        self.narrowerSet = OrderedSet()
        self.supportedLang.append('de')
        self.supportedLang.append('en')

        if language in self.supportedLang:
            apiLang = None
            if language == 'en':
                apiLang = 'en_US'
            elif language == 'de':
                apiLang = 'de_DE'

            for word in self.searchTerms:
                self.runAPICall(word, apiLang)

    @retry(Exception, tries=3)
    def apiCall(self, word, apiLang):
        key = 0
        result = requests.get(self.apiStr + word + self.keySuffix + self.apiKeys[key] + self.langSuffix + apiLang)
        while(result.status_code == 403 and key < len(self.apiKeys)): # Forbidden 403: No permission, or key over rate limit
            key = key + 1
            result = requests.get(self.apiStr + word + self.keySuffix + self.apiKeys[key] + self.langSuffix + apiLang)
        return result

    def runAPICall(self, word, apiLang):
        result = self.apiCall(word, apiLang)
        if result.status_code < 300: # found some terms
            resultJson = result.json()
            response = resultJson['response']
            for responseList in response:
                lists = responseList['list']
                categoryString = lists['synonyms']
                splitArray = categoryString.split(self.splitChar)
                self.fillToSets(splitArray)

    def fillToSets(self, splitArray):
        for term in splitArray:
            term = term.replace(' (similar term)', '')
            term = term.replace(' (related term)', '')
            term = term.replace(' (umgangssprachlich)', '')
            term = term.replace(' (derb)', '')
            term = term.replace(' (fachsprachlich)', '')
            if not '(antonym)' in term and not '(Antonym)' in term:
                if ' (Oberbegriff)' in term:
                    term = term.replace(' (Oberbegriff)', '')
                    self.broaderSet.append(utils.eszettToSS(term))
                elif ' (Unterbegriff)' in term:
                    term = term.replace(' (Unterbegriff)', '')
                    self.narrowerSet.append(utils.eszettToSS(term))
                else:
                    self.relatedSet.append(utils.eszettToSS(term))


    def getRelated(self):
        return self.relatedSet

    def getNarrower(self):
        return self.narrowerSet

    def getBroader(self):
        return self.broaderSet

    def checkConnection(self):
        response = self.apiCall('Test', 'de_DE')
        if response is not None and response.status_code < 300:
            return True
        return False

if __name__ == '__main__':
    av = Altervista('Test', 'de')

    print "Related: "
    for related in av.getRelated():
        print related

    print "\nNarrower: "
    for narrower in av.getNarrower():
        print narrower

    print "\nBroader: "
    for broader in av.getBroader():
        print broader

    print av.checkConnection()