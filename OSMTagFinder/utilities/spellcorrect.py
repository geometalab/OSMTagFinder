# -*- coding: utf-8 -*-
'''
Created on 03.10.2014

@author: Simon Gwerder
'''

# Note: Might wanna checkout GNU Aspell for an alternative library to PyEnchant.
# GNU Aspell also provides dictionaries in more languages.

from utilities import utils

import whoosh.index as index
from whoosh.index import open_dir

class SpellCorrect():
    '''SpellCorrect provides means to get a candidate list for a 'fuzzy search'. Could be used for spell correction too'''

    ix = None

    def __init__(self):
        if not index.exists_in(utils.indexerDir(), utils.indexName):
            return
        self.ix = open_dir(utils.indexerDir(), indexname=utils.indexName)


    def mergeLists(self, first_list, second_list):
        '''Merges the two lists 'first_list' and 'second_list', removing duplicate items'''
        return first_list + list(set(second_list) - set(first_list))

    def listSuggestionsEN(self, word):
        '''Gives a list of EN suggestions for 'word'.'''
        if self.ix is None: return []
        corrector = self.ix.searcher().corrector("spellingEN")
        return corrector.suggest(word, limit=10)


    def listSuggestionsDE(self, word):
        '''Gives a list DE of suggestions for 'word'.'''
        if self.ix is None: return []
        corrector = self.ix.searcher().corrector("spellingDE")
        return corrector.suggest(word, limit=10)


    def listSuggestions(self, word):
        '''Gives a list of suggestions for 'word'.'''
        if self.ix is None: return []
        suggestionsDE = self.listSuggestionsDE(word)
        suggestionsEN = self.listSuggestionsEN(word)
        return self.mergeLists(suggestionsDE, suggestionsEN)


if __name__ == '__main__':
    fw = SpellCorrect()
    print fw.listSuggestionsEN('tabacco')
    print fw.listSuggestionsDE('adres')

