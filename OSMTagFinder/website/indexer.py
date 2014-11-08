# -*- coding: utf-8 -*-
'''
Created on 11.10.2014

@author: Simon Gwerder
'''
from whoosh.index import create_in
import whoosh.index as index
from whoosh.fields import TEXT, ID, NGRAM, Schema
from utilities import utils
from rdflib.namespace import SKOS
from thesaurus.rdfgraph import RDFGraph

class Indexer:

    schema = Schema(subject=ID(stored=True),
                    prefLabel=NGRAM(stored=True),
                    altLabel=NGRAM(stored=True),
                    hiddenLabel=NGRAM(stored=True),
                    scopeNote=TEXT(stored=False))

    __writer = None

    def __init__(self, rdfGraph):
        self.createNewIndex()

        count = 0
        for subject, predicate, obj in rdfGraph.graph:
            if predicate == SKOS.prefLabel:
                print str(count) + ': Indexing prefLabel: ' + str(obj)
                count += 1
                self.addPrefLabel(subject, obj)
            elif predicate == SKOS.altLabel:
                print str(count) + ': Indexing altLabel: ' + str(obj)
                count += 1
                self.addAltLabel(subject, obj)
            elif predicate == SKOS.hiddenLabel:
                print str(count) + ': Indexing hiddenLabel: ' + str(obj)
                count += 1
                self.addHiddenLabel(subject, obj)
            elif predicate == SKOS.scopeNote:
                print str(count) + ': Indexing scopeNote: ' + str(obj)
                count += 1
                self.addScopeNote(subject, obj)

        self.commit()



    def createNewIndex(self):
        ix = create_in(utils.indexerDir(), self.schema, indexname=utils.indexName)
        self.__writer = ix.writer()

    def addPrefLabel(self, subject, prefLabel):
        if not index.exists_in(utils.indexerDir(), utils.indexName):
            self.createNewIndex()
        self.__writer.add_document(subject=unicode(subject), prefLabel=unicode(prefLabel))

    def addAltLabel(self, subject, altLabel):
        if not index.exists_in(utils.indexerDir(), utils.indexName):
            self.createNewIndex()
        self.__writer.add_document(subject=unicode(subject), altLabel=unicode(altLabel))

    def addHiddenLabel(self, subject, hiddenLabel):
        if not index.exists_in(utils.indexerDir(), utils.indexName):
            self.createNewIndex()
        self.__writer.add_document(subject=unicode(subject), hiddenLabel=unicode(hiddenLabel))

    def addScopeNote(self, subject, scopeNote):
        if not index.exists_in(utils.indexerDir(), utils.indexName):
            self.createNewIndex()
        self.__writer.add_document(subject=unicode(subject), scopeNote=unicode(scopeNote))

    def commit(self):
        self.__writer.commit()


if __name__ == '__main__':
    rdfGraph = RDFGraph(utils.dataDir() + 'osm_tag_thesaurus_141107.rdf')
    Indexer(rdfGraph)



