# -*- coding: utf-8 -*-
'''
Created on 11.10.2014

@author: Simon Gwerder
'''
from utilities import utils
from utilities.translator import Translator
from rdflib.namespace import SKOS
from rdflib import Literal
from thesaurus.rdfgraph import RDFGraph

import re
from whoosh.fields import TEXT, ID, Schema
import whoosh.index as index
from whoosh.index import create_in
from utilities.configloader import ConfigLoader

class Indexer:

    schema = Schema(tagSubject=ID(stored=True),
                    tagPrefLabel=TEXT(stored=True),
                    termPrefLabel=TEXT(stored=True),
                    termAltLabel=TEXT(stored=True),
                    termBroader=TEXT(stored=True),
                    termNarrower=TEXT(stored=True),
                    tagScopeNote=TEXT(stored=True),
                    spellingEN=TEXT(stored=True, spelling=True),
                    spellingDE=TEXT(stored=True, spelling=True))

    __writer = None

    wordSetEN = set()
    wordSetDE = set()

    def __init__(self, rdfGraph):
        if rdfGraph is None: return
        self.createNewIndex()

        count = 0
        for subject, predicate, obj in rdfGraph.graph:
            if rdfGraph.isInKeyScheme(subject) or rdfGraph.isInTagScheme(subject):
                if predicate == SKOS.prefLabel:
                    count += 1
                    print str(count) + ': Indexing tagPrefLabel: ' + str(obj)
                    label = utils.wsWord(obj)
                    lit = Literal(label, obj.language)
                    self.addTagPrefLabel(subject, lit)
                elif predicate == SKOS.scopeNote:
                    count += 1
                    print str(count) + ': Indexing tagScopeNote: ' + str(obj)
                    self.addTagScopeNote(subject, obj)

            elif rdfGraph.isInTermScheme(subject):
                tagSubjectList = self.getTagsOfRelTerm(rdfGraph, subject)

                if predicate == SKOS.prefLabel:
                    count += 1
                    lang = obj.language
                    if lang == 'en' or lang == 'de':
                        print str(count) + ': Indexing termPrefLabel: ' + str(obj)
                        self.addTermPrefLabel(tagSubjectList, obj)
                if predicate == SKOS.altLabel:
                    count += 1
                    lang = obj.language
                    if lang == 'en' or lang == 'de':
                        print str(count) + ': Indexing termAltLabel: ' + str(obj)
                        self.addTermAltLabel(tagSubjectList, obj)
                if predicate == SKOS.broader:
                    count += 1
                    lang = obj.language
                    if lang == 'en' or lang == 'de':
                        print str(count) + ': Indexing termBroader: ' + str(obj)
                        self.addTermBroader(tagSubjectList, obj)
                if predicate == SKOS.narrower:
                    count += 1
                    lang = obj.language
                    if lang == 'en' or lang == 'de':
                        print str(count) + ': Indexing termNarrower: ' + str(obj)
                        self.addTermNarrower(tagSubjectList, obj)

        self.addSpellings()

        self.commit()

    splitChars = re.compile('[ ="._,:;/\?\(\)\]\[\!\*]')
    def addToWordList(self, words, filterShort=None):
        lang = words.language
        wordList = self.splitChars.split(words)
        for word in wordList:
            if len(word) <= 1:
                continue;

            if filterShort and len(word) <= filterShort: # skips short lowercased words if 'filterShort'
                continue;

            if lang == 'en':
                word = utils.eszettToSS(word)
                self.wordSetEN.add(word)
            elif lang == 'de':
                word = utils.eszettToSS(word)
                self.wordSetDE.add(word)
            else:
                translator = Translator()
                if not word in self.wordSetDE and word not in self.wordSetEN :
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

    def getTagsOfRelTerm(self, rdfGraph, relTermSubject):
        '''Returns a list of subjects, that point to this RelatedTerm 'subject'.'''
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
        self.addToWordList(tagScopeNote, 5)

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

    def addTermBroader(self, tagSubjectList, termBroader):
        if not index.exists_in(utils.indexerDir(), utils.indexName):
            self.createNewIndex()
        for tagSubject in tagSubjectList:
            self.__writer.add_document(tagSubject=unicode(tagSubject), termBroader=unicode(termBroader))
        self.addToWordList(termBroader)

    def addTermNarrower(self, tagSubjectList, termNarrower):
        if not index.exists_in(utils.indexerDir(), utils.indexName):
            self.createNewIndex()
        for tagSubject in tagSubjectList:
            self.__writer.add_document(tagSubject=unicode(tagSubject), termNarrower=unicode(termNarrower))
        self.addToWordList(termNarrower)

    def commit(self):
        self.__writer.commit()


if __name__ == '__main__':
    cl = ConfigLoader()
    outputName = cl.getThesaurusString('OUTPUT_NAME')
    outputEnding = cl.getThesaurusString('DEFAULT_FORMAT')
    rdfGraph = RDFGraph(utils.outputFile(utils.dataDir(), outputName, outputEnding, useDateEnding=False))
    Indexer(rdfGraph)




