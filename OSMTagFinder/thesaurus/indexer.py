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
from rdfgraph import RDFGraph

class Indexer:

    schema = Schema(concept=ID(stored=True),
                    prefLabel=NGRAM(stored=True),
                    altLabel=NGRAM(stored=True),
                    hiddenLabel=NGRAM(stored=True),
                    scopeNote=TEXT(stored=False))

    __writer = None

    def __init__(self, rdfgraph):
        self.createNewIndex()

        count = 0
        for subject, predicate, obj in rdfgraph.graph:
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

    def addPrefLabel(self, concept, prefLabel):
        if not index.exists_in(utils.indexerDir(), utils.indexName):
            self.createNewIndex()
        self.__writer.add_document(concept=unicode(concept), prefLabel=unicode(prefLabel))

    def addAltLabel(self, concept, altLabel):
        if not index.exists_in(utils.indexerDir(), utils.indexName):
            self.createNewIndex()
        self.__writer.add_document(concept=unicode(concept), altLabel=unicode(altLabel))

    def addHiddenLabel(self, concept, hiddenLabel):
        if not index.exists_in(utils.indexerDir(), utils.indexName):
            self.createNewIndex()
        self.__writer.add_document(concept=unicode(concept), hiddenLabel=unicode(hiddenLabel))

    def addScopeNote(self, concept, scopeNote):
        if not index.exists_in(utils.indexerDir(), utils.indexName):
            self.createNewIndex()
        self.__writer.add_document(concept=unicode(concept), scopeNote=unicode(scopeNote))

    def commit(self):
        self.__writer.commit()


if __name__ == '__main__':
    rg = RDFGraph(utils.dataDir() + 'osm_tag_thesaurus_141017.rdf')
    Indexer(rg)



