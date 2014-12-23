# -*- coding: utf-8 -*-
'''
Created on 12.10.2014

@author: Simon Gwerder
'''
from utilities import utils
from utilities.spellcorrect import SpellCorrect
from utilities.translator import Translator
from utilities.configloader import ConfigLoader

from collections import OrderedDict
from whoosh.qparser import QueryParser
#from whoosh.qparser import MultifieldParser
import whoosh.index as index
from whoosh.index import open_dir
import re
from search.tagresults import TagResults

class GraphSearch:

    threshold = ConfigLoader().getWebsiteInt('THRESHOLD')
    ix = None

    def __init__(self):
        if not index.exists_in(utils.indexerDir(), utils.indexName):
            return
        self.ix = open_dir(utils.indexerDir(), indexname=utils.indexName)

    def search(self, word, searcher, indexerField):
        if self.ix is None or searcher is None:
            return None
        query = QueryParser(indexerField, self.ix.schema).parse(unicode(word))
        return searcher.search(query, limit=None, terms=True)

    def extendedSearch(self, word, searcher, indexerField, results, allHits):
        hits = self.search(word, searcher, indexerField)
        self.updateResults(results, hits)
        return self.upgradeAndExtend(allHits, hits)

    def translateWord(self, word, lang=None):
        translatedWord = word
        try:
            if lang is None:
                translatedWord = Translator().translateToEN(word) # guessing language, is slower
            elif lang=='de':
                translatedWord = Translator().translateDEtoEN(word)
            elif lang=='en':
                translatedWord = Translator().translateENtoDE(word)
        except:
            pass
        return translatedWord

    splitChars = re.compile('[ =._,:;/\?\(\)\]\[\!\*]')
    def translateText(self, words, lang=None):
        wordList = self.splitChars.split(words)
        translatedWords = ''
        for word in wordList:
            if len(word) <= 1:
                continue;
            if word[0] == '"' and word[len(word) - 1] == '"': # don't translate this one
                translatedWords = translatedWords + word
            else:
                translatedWords = translatedWords + self.translateWord(word, lang)
        return utils.wsWord(translatedWords)

    def getSortedTagResults(self, rdfGraph, rawResults):
        tagResults = TagResults(rdfGraph, rawResults)
        return tagResults.getResults()

    def fullSearch(self, rdfGraph, words, lang=None):
        if words is None: return None

        results = OrderedDict()

        containsQuotes = words.count('"') >= 2

        translatedWords = self.translateText(words, lang)
        words = utils.wsWord(words) # do this after translation
        # words and translatedWords are now "whitespaced", containging mostly whitespace separator

        # don't leave the following statement until all results are copied into another datastructure,
        # otherwise the reader is closed.
        with self.ix.searcher() as searcher:

            allHits = None # only to get the correct whoosh score

            allHits = self.extendedSearch(words, searcher, 'termPrefLabel', results, allHits)
            allHits = self.extendedSearch(words, searcher, 'termAltLabel', results, allHits)

            #if allHits is None or len(results) < self.threshold: # in this case, searching with translated words too
            allHits = self.extendedSearch(translatedWords, searcher, 'termPrefLabel', results, allHits)
            allHits = self.extendedSearch(translatedWords, searcher, 'termAltLabel', results, allHits)

            if lang == 'en':
                allHits = self.extendedSearch(words, searcher, 'tagPrefLabel', results, allHits) # english first
                allHits = self.extendedSearch(translatedWords, searcher, 'tagPrefLabel', results, allHits)
            else:
                allHits = self.extendedSearch(translatedWords, searcher, 'tagPrefLabel', results, allHits)  # english first too
                allHits = self.extendedSearch(words, searcher, 'tagPrefLabel', results, allHits)

            allHits = self.extendedSearch(words, searcher, 'termNarrower', results, allHits) # Note: Searching in termNarrower gives me all broader for this term
            allHits = self.extendedSearch(words, searcher, 'termBroader', results, allHits)
            allHits = self.extendedSearch(translatedWords, searcher, 'termNarrower', results, allHits)
            allHits = self.extendedSearch(translatedWords, searcher, 'termBroader', results, allHits)

            if lang == 'en' and (allHits is None or len(results) < self.threshold):
                allHits = self.extendedSearch(words, searcher, 'tagScopeNote', results, allHits)  # english first
                allHits = self.extendedSearch(translatedWords, searcher, 'tagScopeNote', results, allHits)
            elif allHits is None or len(results) < self.threshold:
                allHits = self.extendedSearch(translatedWords, searcher, 'tagScopeNote', results, allHits)  # english first too
                allHits = self.extendedSearch(words, searcher, 'tagScopeNote', results, allHits)

            if not containsQuotes and (allHits is None or len(results) < self.threshold):
                suggestions = SpellCorrect().listSuggestions(words) # is slow
                suggestions.extend(SpellCorrect().listSuggestions(translatedWords))
                for s in suggestions:
                    allHits = self.extendedSearch(s, searcher, 'termPrefLabel', results, allHits)
                    allHits = self.extendedSearch(s, searcher, 'termAltLabel', results, allHits)
                    allHits = self.extendedSearch(s, searcher, 'tagPrefLabel', results, allHits)

                if len(results) < self.threshold:
                    for s in suggestions:
                        allHits = self.extendedSearch(s, searcher, 'tagScopeNote', results, allHits)

            results = self.updateScore(results, allHits)

        return self.getSortedTagResults(rdfGraph, results)

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

                for searchedField in searchMeta: # making sure that the searchTerm lists are unique
                    searchTerms = searchMeta[searchedField]
                    searchMeta[searchedField] = utils.uniquifyList(searchTerms)

                results[subject] = searchMeta
        return results



