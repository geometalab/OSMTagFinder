# -*- coding: utf-8 -*-
'''
Created on 12.10.2014

@author: Simon Gwerder
'''
import socket
from ordered_set import OrderedSet

from whoosh.qparser import QueryParser
from whoosh.index import open_dir
import whoosh.index as index
from utilities.spellcorrect import SpellCorrect
from utilities.translator import Translator
from rdfgraph import RDFGraph
from tagresults import TagResults
from utilities import utils

class GraphSearch:

    threshold = 2

    def prepareWord(self, word):
        word = word.replace('"', ' ')
        word = word.replace(',', ' ')
        word = word.replace(';', ' ')
        word = word.replace(' = ', '=')
        return word

    def search(self, word, includeScopeNote=False, translateDEToEN=False):

        retSet = OrderedSet()
        if not index.exists_in(utils.indexerDir(), utils.indexName):
            return retSet

        ix = open_dir(utils.indexerDir(), indexname=utils.indexName)

        with ix.searcher() as searcher:

            if translateDEToEN:
                try:
                    word = Translator().translateDEtoEN(word)
                except socket.timeout:
                    pass

            queryPrefLabel = QueryParser("prefLabel", ix.schema).parse(unicode(word))
            queryAltLabel = QueryParser("altLabel", ix.schema).parse(unicode(word))
            queryHiddenLabel = QueryParser("hiddenLabel", ix.schema).parse(unicode(word))

            resultsPrefLabel = searcher.search(queryPrefLabel, limit=None, terms=True)
            resultsAltLabel = searcher.search(queryAltLabel, limit=None, terms=True)
            resultsHiddenLabel = searcher.search(queryHiddenLabel, limit=None, terms=True)

            for result in resultsPrefLabel:
                retSet.add(result['subject'])

            for result in resultsAltLabel:
                retSet.add(result['subject'])

            for result in resultsHiddenLabel:
                retSet.add(result['subject'])

            if includeScopeNote:
                queryScopeNote = QueryParser("scopeNote", ix.schema).parse(unicode(word))
                resultsScopeNote = searcher.search(queryScopeNote, limit=None, terms=True)
                for result in resultsScopeNote:
                    retSet.add(result['subject'])

        return retSet

    def extendedSearch(self, word):

        word = self.prepareWord(word)

        results = OrderedSet()
        results = results | self.search(word, includeScopeNote=False, translateDEToEN=False)

        if len(results) < self.threshold:
            results = results | self.search(word, includeScopeNote=False, translateDEToEN=True)

        if len(results) < self.threshold:
            results = results | self.search(word, includeScopeNote=True, translateDEToEN=False)

        if len(results) < self.threshold:
            results = results | self.search(word, includeScopeNote=True, translateDEToEN=True)

        if len(results) < self.threshold:
            suggestions = SpellCorrect().listSuggestions(word)
            for s in suggestions:
                results = results | self.search(s, includeScopeNote=False, translateDEToEN=True)

        if len(results) < self.threshold:
            suggestions = SpellCorrect().listSuggestions(word)
            for s in suggestions:
                results = results | self.search(s, includeScopeNote=True, translateDEToEN=True)

        return results

if __name__ == '__main__':

    rdfGraph = RDFGraph(utils.dataDir() + 'osm_tag_thesaurus_141018.rdf')
    gs = GraphSearch()
    while True:
        word = raw_input("Enter word to search for: ")
        rawResults = gs.extendedSearch(word)
        searchResults = TagResults(rdfGraph, rawResults)





