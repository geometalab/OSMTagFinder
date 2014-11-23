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
                    tagPrefLabel=NGRAM(stored=True),
                    termPrefLabel=TEXT(stored=True),
                    termAltLabel=TEXT(stored=True),
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
                altLabelTermTags = self.tagsOfAltLabelTerm(rdfGraph, subject)

                if predicate == SKOS.prefLabel:
                    count += 1
                    lang = obj.language
                    if lang == 'en' or lang == 'de':
                        print str(count) + ': Indexing termPrefLabel: ' + str(obj)
                        self.addTermPrefLabel(altLabelTermTags, obj)
                if predicate == SKOS.altLabel:
                    count += 1
                    lang = obj.language
                    if lang == 'en' or lang == 'de':
                        print str(count) + ': Indexing termAltLabel: ' + str(obj)
                        self.addTermAltLabel(altLabelTermTags, obj)

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

    def tagsOfAltLabelTerm(self, rdfGraph, relTermSubject):
        generatorList = rdfGraph.getRelatedMatch(relTermSubject)
        return utils.genToList(generatorList)

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

    def addTermPrefLabel(self, tagSubjectList, termPrefLabel):
        if not index.exists_in(utils.indexerDir(), utils.indexName):
            self.createNewIndex()
        for tagSubject in tagSubjectList:
            self.__writer.add_document(tagSubject=unicode(tagSubject), termPrefLabel=unicode(termPrefLabel))
        self.addToWordList(termPrefLabel)

    def addTermAltLabel(self, tagSubjectList, termAltLabel):
        if not index.exists_in(utils.indexerDir(), utils.indexName):
            self.createNewIndex()
        for tagSubject in tagSubjectList:
            self.__writer.add_document(tagSubject=unicode(tagSubject), termAltLabel=unicode(termAltLabel))
        self.addToWordList(termAltLabel)

    def commit(self):
        self.__writer.commit()


if __name__ == '__main__':
    rdfGraph = RDFGraph(utils.dataDir() + 'tagfinder_thesaurus.rdf')
    Indexer(rdfGraph)



