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

    schema = Schema(tagSubject=ID(stored=True),
                    termSubject=ID(stored=True),
                    tagPrefLabel=NGRAM(stored=True),
                    termPrefLabelEN=NGRAM(stored=True),
                    termPrefLabelDE=NGRAM(stored=True),
                    termAltLabelEN=NGRAM(stored=True),
                    termAltLabelDE=NGRAM(stored=True),
                    tagScopeNote=TEXT(stored=True),
                    spellingEN=TEXT(stored=True, spelling=True),
                    spellingDE=TEXT(stored=True, spelling=True))

    __writer = None

    wordSetEN = set()
    wordSetDE = set()

    def __init__(self, rdfGraph):
        self.createNewIndex()

        count = 0
        for subject, predicate, obj in rdfGraph.graph:
            if rdfGraph.isInKeyScheme(subject) or rdfGraph.isInTagScheme(subject):
                if predicate == SKOS.prefLabel:
                    count += 1
                    print str(count) + ': Indexing tagPrefLabel: ' + str(obj)
                    self.addTagPrefLabel(subject, obj)
                elif predicate == SKOS.scopeNote:
                    count += 1
                    print str(count) + ': Indexing tagScopeNote: ' + str(obj)
                    self.addTagScopeNote(subject, obj)
            elif rdfGraph.isInTermScheme(subject):
                if predicate == SKOS.prefLabel:
                    count += 1
                    lang = obj.language
                    if lang == 'en':
                        print str(count) + ': Indexing termPrefLabelEN: ' + str(obj)
                        self.addTermPrefLabelEN(subject, obj)
                    elif lang == 'de':
                        print str(count) + ': Indexing termPrefLabelDE: ' + str(obj)
                        self.addTermPrefLabelDE(subject, obj)
                if predicate == SKOS.altLabel:
                    count += 1
                    lang = obj.language
                    if lang == 'en':
                        print str(count) + ': Indexing termAltLabelEN: ' + str(obj)
                        self.addTermAltLabelEN(subject, obj)
                    elif lang == 'de':
                        print str(count) + ': Indexing termAltLabelDE: ' + str(obj)
                        self.addTermAltLabelDE(subject, obj)

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

    def addTagPrefLabel(self, tagSubject, tagPrefLabel):
        if not index.exists_in(utils.indexerDir(), utils.indexName):
            self.createNewIndex()
        self.__writer.add_document(tagSubject=unicode(tagSubject), tagPrefLabel=unicode(tagPrefLabel))
        self.addToWordList(tagPrefLabel)

    def addTagScopeNote(self, tagSubject, tagScopeNote):
        if not index.exists_in(utils.indexerDir(), utils.indexName):
            self.createNewIndex()
        self.__writer.add_document(tagSubject=unicode(tagSubject), tagScopeNote=unicode(tagScopeNote))
        self.addToWordList(tagScopeNote)

    def addTermPrefLabelEN(self, termSubject, termPrefLabelEN):
        if not index.exists_in(utils.indexerDir(), utils.indexName):
            self.createNewIndex()
        self.__writer.add_document(termSubject=unicode(termSubject), termPrefLabelEN=unicode(termPrefLabelEN))
        self.addToWordList(termPrefLabelEN)

    def addTermPrefLabelDE(self, termSubject, termPrefLabelDE):
        if not index.exists_in(utils.indexerDir(), utils.indexName):
            self.createNewIndex()
        self.__writer.add_document(termSubject=unicode(termSubject), termPrefLabelDE=unicode(termPrefLabelDE))
        self.addToWordList(termPrefLabelDE)

    def addTermAltLabelEN(self, termSubject, termAltLabelEN):
        if not index.exists_in(utils.indexerDir(), utils.indexName):
            self.createNewIndex()
        self.__writer.add_document(termSubject=unicode(termSubject), termAltLabelEN=unicode(termAltLabelEN))
        self.addToWordList(termAltLabelEN)

    def addTermAltLabelDE(self, termSubject, termAltLabelDE):
        if not index.exists_in(utils.indexerDir(), utils.indexName):
            self.createNewIndex()
        self.__writer.add_document(termSubject=unicode(termSubject), termAltLabelDE=unicode(termAltLabelDE))
        self.addToWordList(termAltLabelDE)

    def commit(self):
        self.__writer.commit()


if __name__ == '__main__':
    rdfGraph = RDFGraph(utils.dataDir() + 'tagfinder_thesaurus.rdf')
    Indexer(rdfGraph)



