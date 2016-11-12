# -*- coding: utf-8 -*-
'''
Created on 03.10.2014

@author: Simon Gwerder
'''

# Note: Might wanna checkout GNU Aspell for an alternative library to PyEnchant.
# GNU Aspell also provides dictionaries in more languages.

import re

import whoosh.index as index
from utilities import utils
from whoosh.index import open_dir

class SpellCorrect():
    '''SpellCorrect provides means to get a candidate list for a 'fuzzy search'. Useable for type-ahead aswell'''

    ix = None

    limit = 5 # 8 is boostrap default

    def __init__(self):
        if not index.exists_in(utils.indexerDir(), utils.indexName):
            return
        self.ix = open_dir(utils.indexerDir(), indexname=utils.indexName)

    splitChars = re.compile('[ =".,:;/\?\(\)\]\[\!\*]')
    def splitWords(self, word):
        return self.splitChars.split(word)

    def mergeLists(self, first_list, second_list):
        '''Merges the two lists 'first_list' and 'second_list', removing duplicate items'''
        return first_list + list(set(second_list) - set(first_list))

    def listSuggestionsEN(self, word):
        '''Gives a list of EN suggestions for 'word'. Empty list if none found.'''
        if self.ix is None or word is None or word == '': return []
        retList = []
        corrector = self.ix.searcher().corrector("spellingEN")
        wordList = self.splitWords(word.lower())
        for singleWord in wordList:
            retList = self.mergeLists(retList, corrector.suggest(singleWord, limit=self.limit, maxdist=2))
        return retList


    def listSuggestionsDE(self, word):
        '''Gives a list DE of suggestions for 'word'. Empty list if none found.'''
        if self.ix is None or word is None or word == '': return []
        retList = []
        corrector = self.ix.searcher().corrector("spellingDE")
        wordList = self.splitWords(word.lower())
        for singleWord in wordList:
            retList = self.mergeLists(retList, corrector.suggest(singleWord, limit=self.limit, maxdist=2))
        return retList


    def listSuggestions(self, word):
        '''Gives a list of suggestions for 'word'. Empty list if none found.'''
        if self.ix is None: return []
        suggestionsDE = self.listSuggestionsDE(word)
        suggestionsEN = self.listSuggestionsEN(word)
        return self.mergeLists(suggestionsDE, suggestionsEN)


if __name__ == '__main__':
    fw = SpellCorrect()
    print fw.listSuggestionsEN('tabacco')
    print fw.listSuggestionsDE('adres zoo')

