# -*- coding: utf-8 -*-
'''
Created on 01.11.2014

@author: Simon Gwerder
'''
from thesauribase import ThesauriBase
from utilities import utils
from utilities.configloader import ConfigLoader
from utilities.retry import retry

from wordnik import swagger, WordApi
from ordered_set import OrderedSet

class WordnikApi(ThesauriBase):

    cl = ConfigLoader()
    apiUrl = cl.getWordnikAPIString('API_URL')
    apiKey = 'f56e0ac9bcfd011dcf15f07382b057da68ece00811dcb38a9' # 15000 queries per hour


    relatedSet = OrderedSet()
    broaderSet = OrderedSet()
    narrowerSet = OrderedSet()

    # dont retry here: @retry(Exception, tries=3)
    def apiCall(self, word, apiLang):
        client = swagger.ApiClient(self.apiKey, self.apiUrl)
        wordApi = WordApi.WordApi(client)
        relatedWords = wordApi.getRelatedWords(word)
        return relatedWords

    def __init__(self, searchTerm, language):
        ThesauriBase.__init__(self, searchTerm, language)
        self.relatedSet = OrderedSet()
        self.broaderSet = OrderedSet()
        self.narrowerSet = OrderedSet()
        self.supportedLang.append('en')

        if language in self.supportedLang:
            for word in self.searchTerms:
                relatedWords = self.apiCall(word, language)
                if relatedWords is not None:
                    for related in relatedWords:
                        relationship = related.relationshipType
                        if ('equivalent' in relationship or 'synonym' in relationship
                        or 'verb-form' in relationship or 'form' in relationship):
                            for word in related.words:
                                self.relatedSet.append(utils.eszettToSS(word))
                        if('hypernym' in relationship):
                            for word in related.words:
                                self.broaderSet.append(utils.eszettToSS(word))
                        if('hyponym' in relationship):
                            for word in related.words:
                                self.narrowerSet.append(utils.eszettToSS(word))

    def getRelated(self):
        return self.relatedSet

    def getNarrower(self):
        return self.narrowerSet

    def getBroader(self):
        return self.broaderSet

    def checkConnection(self):
        try:
            client = swagger.ApiClient(self.apiKey, self.apiUrl)
            wordApi = WordApi.WordApi(client)
            wordApi.getRelatedWords('test')
            return True
        except:
            return False

if __name__ == '__main__':
    wa = WordnikApi('hairdresser', 'en')

    print "Related: "
    for related in wa.getRelated():
        print related

    print "\nNarrower: "
    for narrower in wa.getNarrower():
        print narrower

    print "\nBroader: "
    for broader in wa.getBroader():
        print broader