# -*- coding: utf-8 -*-
'''
Created on 12.10.2014

@author: Simon Gwerder
'''

from whoosh.qparser import QueryParser
from whoosh.index import open_dir
import whoosh.index as index
from utilities.spellcorrect import SpellCorrect
from utilities.translator import Translator
from rdfgraph import RDFGraph
from ordered_set import OrderedSet

from utilities import utils

class GraphSearch:

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
                word = Translator().translateDEtoEN(word)

            queryPrefLabel = QueryParser("prefLabel", ix.schema).parse(unicode(word))
            queryAltLabel = QueryParser("altLabel", ix.schema).parse(unicode(word))
            queryHiddenLabel = QueryParser("hiddenLabel", ix.schema).parse(unicode(word))

            resultsPrefLabel = searcher.search(queryPrefLabel, limit=None, terms=True)
            resultsAltLabel = searcher.search(queryAltLabel, limit=None, terms=True)
            resultsHiddenLabel = searcher.search(queryHiddenLabel, limit=None, terms=True)

            for result in resultsPrefLabel:
                retSet.add(result['concept'])

            for result in resultsAltLabel:
                retSet.add(result['concept'])

            for result in resultsHiddenLabel:
                retSet.add(result['concept'])

            if includeScopeNote:
                queryScopeNote = QueryParser("scopeNote", ix.schema).parse(unicode(word))
                resultsScopeNote = searcher.search(queryScopeNote, limit=None, terms=True)
                for result in resultsScopeNote:
                    retSet.add(result['concept'])

        return retSet

    def extendedSearch(self, word):

        word = self.prepareWord(word)

        threshold = 2

        results = OrderedSet()
        results = results | gs.search(word, includeScopeNote=False, translateDEToEN=False)

        if len(results) < threshold:
            results = results | gs.search(word, includeScopeNote=False, translateDEToEN=True)

        if len(results) < threshold:
            results = results | gs.search(word, includeScopeNote=True, translateDEToEN=False)

        if len(results) < threshold:
            results = results | gs.search(word, includeScopeNote=True, translateDEToEN=True)

        if len(results) < threshold:
            suggestions = SpellCorrect().listSuggestions(word)
            for s in suggestions:
                results = results | gs.search(s, includeScopeNote=False, translateDEToEN=True)

        if len(results) < threshold:
            suggestions = SpellCorrect().listSuggestions(word)
            for s in suggestions:
                results = results | gs.search(s, includeScopeNote=True, translateDEToEN=True)

        return results




if __name__ == '__main__':
    rg = RDFGraph(utils.dataDir() + 'osm_tag_thesaurus_141017.rdf')

    gs = GraphSearch()
    while True:
        word = raw_input("Enter word to search for: ")
        partResults = gs.extendedSearch(word)
        for subject in partResults:
            print('\t' + str(subject))

            prefLabelGen = rg.getPrefLabels(subject)
            broaderGen = rg.getBroader(subject)
            narrowerGen = rg.getNarrower(subject)
            depictionGen = rg.getDepiction(subject)
            scopeNoteGen = rg.getScopeNote(subject)

            for item in prefLabelGen:
                print('\t\tprefLabel: ' + str(item))

            for item in broaderGen:
                print('\t\tbroader: ' + str(item))

            for item in narrowerGen:
                print('\t\tnarrower: ' + str(item))

            for item in depictionGen:
                print('\t\tdepicition: ' + str(item))

            for item in scopeNoteGen:
                print('\t\tscopeNote: ' + str(item))



