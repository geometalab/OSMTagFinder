# -*- coding: utf-8 -*-
'''
Created on 01.11.2014

@author: Simon Gwerder
'''
from ordered_set import OrderedSet

from altervista import Altervista
from gemet import Gemet
from openthesaurus import OpenThesaurus
from wordnikapi import WordnikApi


class Vocabulary:

    relatedSet = OrderedSet()
    broaderSet = OrderedSet()
    narrowerSet = OrderedSet()

    gemet = None
    altervista = None
    wordnik = None
    openthesaurus = None

    def __init__(self, word, language):
        self.gemet = Gemet(word, language)
        self.altervista = Altervista(word, language)
        self.wordnik = WordnikApi(word, language)
        self.openthesaurus = OpenThesaurus(word, language)

        self.callThesauri(self.gemet)
        self.callThesauri(self.altervista)
        self.callThesauri(self.wordnik)
        self.callThesauri(self.openthesaurus)

        self.removeRelatedWord(word) # making sure no self relation occurs

    def checkConGemet(self):
        return self.gemet.checkConnection()

    def checkConAltervista(self):
        return self.altervista.checkConnection()

    def checkConOpenThesaurus(self):
        return self.openthesaurus.checkConnection()

    def checkConWordnik(self):
        return self.wordnik.checkConnection()

    def removeRelatedWord(self, word):
        if word in self.relatedSet:
            temp = []
            for related in self.relatedSet:
                temp.append(related)
            temp.remove(word)
            self.relatedSet = OrderedSet() | temp

    def callThesauri(self, thesauri):
        self.relatedSet  = self.relatedSet  | thesauri.getRelated()
        self.broaderSet  = self.broaderSet  | thesauri.getBroader()
        self.narrowerSet = self.narrowerSet | thesauri.getNarrower()


    def getRelated(self):
        '''Returns an ordered set containing all synonyms and other related terms for 'searchTerm'.'''
        return self.relatedSet

    def getNarrower(self):
        '''Returns an ordered set containing all narrower terms for 'searchTerm'. this > result'''
        return self.narrowerSet

    def getBroader(self):
        '''Returns an ordered set containing all broader terms for 'searchTerm'. this < result'''
        return self.broaderSet


if __name__ == '__main__':
    t = Vocabulary('rail', 'en')

    print "Related: "
    relatedStr = ''
    for related in t.getRelated():
        relatedStr = relatedStr + related + ', '
    print relatedStr

    print "\nNarrower: "
    narrowerStr = ''
    for narrower in t.getNarrower():
        narrowerStr = narrowerStr + narrower + ', '
    print narrowerStr

    print "\nBroader: "
    broaderStr = ''
    for broader in t.getBroader():
        broaderStr = broaderStr + broader + ', '
    print broaderStr



