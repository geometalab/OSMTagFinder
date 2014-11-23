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

    def search(self, word, searcher, indexerField):
        if self.ix is None or searcher is None:
            return None
        query = QueryParser(indexerField, self.ix.schema).parse(unicode(word))
        return searcher.search(query, limit=None, terms=True)

    def extendedSearch(self, word, searcher, indexerField, results, allHits):
        hits = self.search(word, searcher, indexerField)
        self.updateResults(results, hits)
        return self.upgradeAndExtend(allHits, hits)

    def fullSearch(self, word, localDE=False):
        results = OrderedDict()
        word = self.prepareWord(word)
        translatedWord = word

        if localDE:
            try:
                translatedWord = Translator().translateDEtoEN(word)
            except:
                pass

        # don't leave the following statement until all results are copied into another datastructure,
        # otherwise the reader is closed.
        with self.ix.searcher() as searcher:

            allHits = None # only to get the correct whoosh score

            '''if not localDE and (allHits is None or allHits.scored_length() < self.threshold):'''
            allHits = self.extendedSearch(word, searcher, 'termPrefLabel', results, allHits)
            '''elif localDE and (allHits is None or allHits.scored_length() < self.threshold):
                allHits = self.extendedSearch(translatedWord, searcher, 'termPrefLabel', results, allHits)'''

            '''if not localDE and (allHits is None or allHits.scored_length() < self.threshold):'''
            allHits = self.extendedSearch(word, searcher, 'termAltLabel', results, allHits)
            '''elif localDE and (allHits is None or allHits.scored_length() < self.threshold):
                allHits = self.extendedSearch(translatedWord, searcher, 'termAltLabel', results, allHits)'''

            if not localDE and (allHits is None or allHits.scored_length() < self.threshold):
                allHits = self.extendedSearch(word, searcher, 'tagPrefLabel', results, allHits)
            elif localDE and (allHits is None or allHits.scored_length() < self.threshold):
                allHits = self.extendedSearch(translatedWord, searcher, 'tagPrefLabel', results, allHits)

            if not localDE and (allHits is None or allHits.scored_length() < self.threshold):
                allHits = self.extendedSearch(word, searcher, 'tagScopeNote', results, allHits)
            elif localDE and (allHits is None or allHits.scored_length() < self.threshold):

                allHits = self.extendedSearch(translatedWord, searcher, 'tagScopeNote', results, allHits)

            if allHits is None or allHits.scored_length() < self.threshold:
                suggestions = SpellCorrect().listSuggestions(word)
                for s in suggestions:
                    allHits = self.extendedSearch(s, searcher, 'tagPrefLabel', results, allHits)

                if allHits.scored_length() < self.threshold:
                    for s in suggestions:
                        allHits = self.extendedSearch(s, searcher, 'tagScopeNote', results, allHits)

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
            subject = hit['tagSubject']
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
                subject = hit['tagSubject']
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





