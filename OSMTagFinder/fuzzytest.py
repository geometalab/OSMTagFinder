'''
Created on 03.10.2014

@author: Simon Gwerder
'''

#Note: Might wanna checkout GNU Aspell for an alternative library to PyEnchant.
# GNU Aspell also provides dictionaries in more languages.

import enchant

class FuzzyWord():

    dictEN_GB = enchant.Dict('en_GB')
    dictEN_US = enchant.Dict('en_US')
    dictDE_DE = enchant.Dict('de_DE')

    def merge_lists(self, first_list, second_list):
        '''Merges the two lists 'first_list' and 'second_list', removing duplicate items'''
        return first_list + list(set(second_list) - set(first_list))

    def list_suggestionsEN(self, word):
        '''Gives a list of suggestions for 'word', based on en_GB, en_US dictionaries'''
        suggestionsGB = self.dictEN_GB.suggest(word)
        suggestionsUS = self.dictEN_US.suggest(word)
        return self.merge_lists(suggestionsGB, suggestionsUS)

    def list_suggetionsDE(self, word):
        '''Gives a list of suggestions for 'word', based on de_DE dictionaries'''
        return self.dictDE_DE.suggest(word)

    def list_suggestions(self, word):
        '''Gives a list of suggestions for 'word', based on en_GB, en_US and de_DE dictionaries'''
        suggestionsGB = self.dictEN_GB.suggest(word)
        suggestionsUS = self.dictEN_US.suggest(word)
        suggestionsDE = self.dictDE_DE.suggest(word)

        return self.merge_lists(suggestionsDE, self.merge_lists(suggestionsGB, suggestionsUS))

if __name__ == '__main__':
    fw = FuzzyWord()

    print fw.list_suggestions('tabacco')
    print fw.list_suggetionsDE('Farad')