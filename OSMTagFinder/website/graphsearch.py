# -*- coding: utf-8 -*-
'''
Created on 12.10.2014

@author: Simon Gwerder
'''
from utilities import utils
from utilities.spellcorrect import SpellCorrect
from utilities.translator import Translator
from thesaurus.rdfgraph import RDFGraph
from tagresults import TagResults

from collections import OrderedDict
from whoosh.qparser import QueryParser
#from whoosh.qparser import MultifieldParser
import whoosh.index as index
from whoosh.index import open_dir

class GraphSearch:

    threshold = 2
    ix = None

    def __init__(self):
        if not index.exists_in(utils.indexerDir(), utils.indexName):
            return
        self.ix = open_dir(utils.indexerDir(), indexname=utils.indexName)

    def prepareWord(self, word):
        word = word.replace('"', ' ')
        word = word.replace(',', ' ')
        word = word.replace(';', ' ')
        word = word.replace(' = ', '=')
        word = utils.eszettToSS(word)
        return word

    def searchPrefLabel(self, word, searcher):
        if self.ix is None or searcher is None:
            return None
        query = QueryParser("prefLabel", self.ix.schema).parse(unicode(word))
        return searcher.search(query, limit=None, terms=True)

    def searchScopeNote(self, word, searcher):
        if self.ix is None or searcher is None:
            return None
        query = QueryParser("scopeNote", self.ix.schema).parse(unicode(word))
        return searcher.search(query, limit=None, terms=True)

    def fullSearch(self, word, translateDEToEN=False):

        results = OrderedDict()

        word = self.prepareWord(word)
        translatedWord = word

        if translateDEToEN:
            try:
                translatedWord = Translator().translateDEtoEN(word)
            except:
                pass

        # don't leave the following statement until all results are copied into another datastructure,
        # otherwise the reader is closed.
        with self.ix.searcher() as searcher:

            allHits = None # only to get the correct whoosh score

            if not translateDEToEN:
                hits = self.searchPrefLabel(word, searcher)
                self.updateResults(results, hits)
                allHits = self.upgradeAndExtend(allHits, hits)

            else:
                hits = self.searchPrefLabel(translatedWord, searcher)
                self.updateResults(results, hits)
                allHits = self.upgradeAndExtend(allHits, hits)

            if not translateDEToEN and len(hits) < self.threshold:
                hits = self.searchScopeNote(word, searcher)
                self.updateResults(results, hits)
                allHits = self.upgradeAndExtend(allHits, hits)

            elif translateDEToEN and len(hits) < self.threshold:
                hits = self.searchScopeNote(translatedWord, searcher)
                self.updateResults(results, hits)
                allHits = self.upgradeAndExtend(allHits, hits)

            if len(hits) < self.threshold:
                suggestions = SpellCorrect().listSuggestions(word)
                for s in suggestions:
                    #s = Translator().translateDEtoEN(word)
                    hits = self.searchPrefLabel(s, searcher)
                    self.updateResults(results, hits)
                    allHits = self.upgradeAndExtend(allHits, hits)

                if len(hits) < self.threshold:
                    for s in suggestions:
                        hits = self.searchScopeNote(s, searcher)
                        self.updateResults(results, hits)
                        allHits = self.upgradeAndExtend(allHits, hits)

            results = self.updateScore(results, allHits)

        return results

    def upgradeAndExtend(self, allHits, hits):
        if allHits is None:
            allHits = hits
        else:
            allHits.upgrade_and_extend(hits)
        return allHits

    def updateScore(self, results, allHits):
        if allHits is None: return results
        for hit in allHits:
            subject = hit['subject']
            searchMeta = { } # temp
            if subject in results:
                searchMeta = results[subject]
                searchMeta['score'] = hit.score
            else:
                searchMeta['score'] = hit.score
            results[subject] = searchMeta
        return results

    def updateResults(self, results, hits):
        if hits is None or not hits.has_matched_terms(): return results
        for hit in hits:
            matchedTerms = hit.matched_terms()
            for matchedPair in matchedTerms:
                searchedField = matchedPair[0]
                searchedTerm = matchedPair[1]
                subject = hit['subject']
                searchMeta = { } # temp
                if subject in results:
                    searchMeta = results[subject]
                    if searchedField in searchMeta:
                        searchTerms = searchMeta[searchedField]
                        searchTerms.append(searchedTerm)
                        searchMeta[searchedField] = searchTerms
                    else:
                        searchMeta[searchedField] = [ searchedTerm ]
                else:
                    searchMeta[searchedField] = [ searchedTerm ]
                results[subject] = searchMeta
        return results


if __name__ == '__main__':

    rdfGraph = RDFGraph(utils.dataDir() + 'tagfinder_thesaurus.rdf')
    gs = GraphSearch()
    while True:
        word = raw_input('Enter word to search for: ')
        rawResults = gs.fullSearch(word)
        searchResults = TagResults(rdfGraph, rawResults)
        for item in searchResults.getResults():
            print '\t' + str(item)





