# -*- coding: utf-8 -*-
'''
Created on 11.10.2014

@author: Simon Gwerder
'''
from utilities import utils
from utilities.translator import Translator
from rdflib.namespace import SKOS
from thesaurus.rdfgraph import RDFGraph

import re
from whoosh.fields import TEXT, ID, NGRAM, Schema
import whoosh.index as index
from whoosh.index import create_in

class Indexer:

    schema = Schema(subject=ID(stored=True),
                    prefLabel=NGRAM(stored=True),
                    altLabel=NGRAM(stored=True),
                    hiddenLabel=NGRAM(stored=True),
                    scopeNote=TEXT(stored=False),
                    spellingEN=TEXT(stored=True, spelling=True),
                    spellingDE=TEXT(stored=True, spelling=True))

    __writer = None

    wordSetEN = set()
    wordSetDE = set()

    def __init__(self, rdfGraph):
        self.createNewIndex()

        count = 0
        for subject, predicate, obj in rdfGraph.graph:
            if predicate == SKOS.prefLabel:
                count += 1
                print str(count) + ': Indexing prefLabel: ' + str(obj)
                self.addPrefLabel(subject, obj)
            elif predicate == SKOS.altLabel:
                count += 1
                print str(count) + ': Indexing altLabel: ' + str(obj)
                self.addAltLabel(subject, obj)
            elif predicate == SKOS.hiddenLabel:
                count += 1
                print str(count) + ': Indexing hiddenLabel: ' + str(obj)
                self.addHiddenLabel(subject, obj)
            elif predicate == SKOS.scopeNote:
                count += 1
                print str(count) + ': Indexing scopeNote: ' + str(obj)
                self.addScopeNote(subject, obj)

        self.addSpellings()

        self.commit()

    splitChars = re.compile('[ =".,:;/\?\(\)\]\[\!\*]')
    def addToWordList(self, words):
        lang = words.language
        wordList = self.splitChars.split(words)
        if lang == 'en':
            for word in wordList:
                if len(word) > 1:
                    word = utils.eszettToSS(word)
                    self.wordSetEN.add(word)
        elif lang == 'de':
            for word in wordList:
                if len(word) > 1:
                    word = utils.eszettToSS(word)
                    self.wordSetDE.add(word)
        else:
            translator = Translator()
            for word in wordList:
                if len(word) > 1 and word not in self.wordSetDE and word not in self.wordSetEN :
                    try:
                        transWordDE = translator.translateENToDE(word)
                        transWordDE = utils.eszettToSS(transWordDE)
                        self.wordSetDE.add(transWordDE)
                        self.wordSetEN.add(utils.eszettToSS(word))
                    except:
                        pass


    def addSpellings(self):
        countEN = 0
        countDE = 0
        for word in self.wordSetEN:
            countEN += 1
            print str(countEN) + ': Indexing EN spelling for word: ' + word
            self.__writer.add_document(spellingEN=unicode(word))

        for word in self.wordSetDE:
            countDE += 1
            print str(countDE) + ': Indexing DE spelling for word: ' + word
            self.__writer.add_document(spellingDE=unicode(word))

    def createNewIndex(self):
        ix = create_in(utils.indexerDir(), self.schema, indexname=utils.indexName)
        self.__writer = ix.writer()

    def addPrefLabel(self, subject, prefLabel):
        if not index.exists_in(utils.indexerDir(), utils.indexName):
            self.createNewIndex()
        self.__writer.add_document(subject=unicode(subject), prefLabel=unicode(prefLabel))
        self.addToWordList(prefLabel)

    def addAltLabel(self, subject, altLabel):
        if not index.exists_in(utils.indexerDir(), utils.indexName):
            self.createNewIndex()
        self.__writer.add_document(subject=unicode(subject), altLabel=unicode(altLabel))
        self.addToWordList(altLabel)

    def addHiddenLabel(self, subject, hiddenLabel):
        if not index.exists_in(utils.indexerDir(), utils.indexName):
            self.createNewIndex()
        self.__writer.add_document(subject=unicode(subject), hiddenLabel=unicode(hiddenLabel))
        self.addToWordList(hiddenLabel)

    def addScopeNote(self, subject, scopeNote):
        if not index.exists_in(utils.indexerDir(), utils.indexName):
            self.createNewIndex()
        self.__writer.add_document(subject=unicode(subject), scopeNote=unicode(scopeNote))
        self.addToWordList(scopeNote)

    def commit(self):
        self.__writer.commit()


if __name__ == '__main__':
    rdfGraph = RDFGraph(utils.dataDir() + 'tagfinder_thesaurus_141116.rdf')
    Indexer(rdfGraph)



