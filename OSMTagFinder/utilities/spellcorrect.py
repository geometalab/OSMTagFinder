# -*- coding: utf-8 -*-
'''
Created on 03.10.2014

@author: Simon Gwerder
'''

# Note: Might wanna checkout GNU Aspell for an alternative library to PyEnchant.
# GNU Aspell also provides dictionaries in more languages.

from enchant import Dict

class SpellCorrect():
    '''SpellCorrect provides means to get a candidate list for a 'fuzzy search'. Could be used for spell correction too'''
    dictEN_GB = Dict('en_GB')
    dictEN_US = Dict('en_US')
    dictDE_DE = Dict('de_DE')
    # dictFR_FR = enchant.Dict('fr_FR')

    def mergeLists(self, first_list, second_list):
        '''Merges the two lists 'first_list' and 'second_list', removing duplicate items'''
        return first_list + list(set(second_list) - set(first_list))

    def listSuggestionsEN(self, word):
        '''Gives a list of suggestions for 'word', based on en_GB, en_US dictionaries'''
        suggestionsGB = self.dictEN_GB.suggest(word)
        suggestionsUS = self.dictEN_US.suggest(word)
        return self.mergeLists(suggestionsGB, suggestionsUS)

    def listSuggestionsDE(self, word):
        '''Gives a list of suggestions for 'word', based on de_DE dictionaries'''
        return self.dictDE_DE.suggest(word)

    # def listSuggestionsFR(self, word):
        # '''Gives a list of suggestions for 'word', based on de_DE dictionaries'''
        # return self.dictFR_FR.suggest(word)

    def listSuggestions(self, word):
        '''Gives a list of suggestions for 'word', based on en_GB, en_US and de_DE dictionaries'''
        suggestionsGB = self.dictEN_GB.suggest(word)
        suggestionsUS = self.dictEN_US.suggest(word)
        suggestionsDE = self.dictDE_DE.suggest(word)

        return self.mergeLists(suggestionsDE, self.mergeLists(suggestionsGB, suggestionsUS))

if __name__ == '__main__':
    fw = SpellCorrect()

    print fw.listSuggestionsEN('tabaco')
    print fw.listSuggestionsDE('Telephon')