# -*- coding: utf-8 -*-
'''
Created on 12.10.2014

@author: Simon Gwerder
'''

from whoosh.qparser import QueryParser
from whoosh.index import open_dir
import whoosh.index as index
from spellcorrect import SpellCorrect

from translator import Translator

import utils

class GraphSearch:

    def uniqueList(self, seq):
        seen = set()
        seen_add = seen.add
        return [ x for x in seq if not (x in seen or seen_add(x))]

    def search(self, word, includeScopeNote=False, translateDEToEN=False):

        retList = []
        if not index.exists_in(utils.indexerDir(), utils.indexName):
            return retList

        ix = open_dir(utils.indexerDir(), indexname=utils.indexName)

        with ix.searcher() as searcher:

            if translateDEToEN:
                word = Translator().translateDEtoEN(word)

            queryPrefLabel = QueryParser("prefLabel", ix.schema).parse(unicode(word))
            queryAltLabel = QueryParser("altLabel", ix.schema).parse(unicode(word))
            queryHiddenLabel = QueryParser("hiddenLabel", ix.schema).parse(unicode(word))
            resultsPrefLabel = searcher.search(queryPrefLabel, limit=None, terms=True)
            resultsAltLabel = searcher.search(queryAltLabel, limit=None, terms=True)
            resultsHiddenLabel = searcher.search(queryHiddenLabel, limit=None, terms=True)

            for result in resultsPrefLabel:
                retList.append(result['concept'])

            for result in resultsAltLabel:
                retList.append(result['concept'])

            for result in resultsHiddenLabel:
                retList.append(result['concept'])

            if includeScopeNote:
                queryScopeNote = QueryParser("scopeNote", ix.schema).parse(unicode(word))
                resultsScopeNote = searcher.search(queryScopeNote, limit=None, terms=True)
                for result in resultsScopeNote:
                    retList.append(result['concept'])

            retList = self.uniqueList(retList)

        return retList


if __name__ == '__main__':

    gs = GraphSearch()
    while True:
        threshold = 2
        word = raw_input("Enter word to search for: ")
        results = set()
        results.update(gs.search(word, includeScopeNote=False, translateDEToEN=False))
        if len(results) < threshold:
            results.update(gs.search(word, includeScopeNote=False, translateDEToEN=True))
        if len(results) < threshold:
            results.update(gs.search(word, includeScopeNote=True, translateDEToEN=False))
        if len(results) < threshold:
            results.update(gs.search(word, includeScopeNote=True, translateDEToEN=True))
        if len(results) < threshold:
            suggestions = SpellCorrect().listSuggestions(word)
            for s in suggestions:
                results.update(gs.search(s, includeScopeNote=False, translateDEToEN=True))
        if len(results) < threshold:
            suggestions = SpellCorrect().listSuggestions(word)
            for s in suggestions:
                results.update(gs.search(s, includeScopeNote=True, translateDEToEN=True))

        for result in results:
            print('\t' + str(result))


