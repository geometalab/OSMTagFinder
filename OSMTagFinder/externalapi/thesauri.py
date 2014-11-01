# -*- coding: utf-8 -*-
'''
Created on 01.11.2014

@author: Simon Gwerder
'''
from gemet import Gemet
from altervista import Altervista
from openthesaurus import OpenThesaurus
from wordnikapi import WordnikApi

from ordered_set import OrderedSet

class Thesauri:

    relatedSet = OrderedSet()
    broaderSet = OrderedSet()
    narrowerSet = OrderedSet()

    def __init__(self, word, language):
        gemet = Gemet(word, language)
        altervista = Altervista(word, language)
        wordnik = WordnikApi(word, language)
        openthesaurus = OpenThesaurus(word, language)

        self.callThesauri(gemet)
        self.callThesauri(altervista)
        self.callThesauri(wordnik)
        self.callThesauri(openthesaurus)

        self.removeRelatedWord(word) # making sure no self relation occurs


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
    t = Thesauri('Fahrrad', 'de')

    print "Related: "
    for related in t.getRelated():
        print related

    print "\nNarrower: "
    for narrower in t.getNarrower():
        print narrower

    print "\nBroader: "
    for broader in t.getBroader():
        print broader



