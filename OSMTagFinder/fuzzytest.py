'''
Created on 03.10.2014

@author: Simon Gwerder
'''
import enchant

dictEN_GB = enchant.Dict('en_GB')
dictEN_US = enchant.Dict('en_US')
dictDE_DE = enchant.Dict('de_DE')

def merge_lists(first_list, second_list):
    '''Merges the two lists 'first_list' and 'second_list', removing duplicate items'''
    return first_list + list(set(second_list) - set(first_list))

def list_suggestionsEN(word):
    '''Gives a list of suggestions for 'word', based on en_GB, en_US dictionaries'''
    suggestionsGB = dictEN_GB.suggest(word)
    suggestionsUS = dictEN_US.suggest(word)
    return merge_lists(suggestionsGB, suggestionsUS)

def list_suggetionsDE(word):
    '''Gives a list of suggestions for 'word', based on de_DE dictionaries'''
    return dictDE_DE.suggest(word)

def list_suggestions(word):
    '''Gives a list of suggestions for 'word', based on en_GB, en_US and de_DE dictionaries'''
    suggestionsGB = dictEN_GB.suggest(word)
    suggestionsUS = dictEN_US.suggest(word)
    suggestionsDE = dictDE_DE.suggest(word)

    return merge_lists(suggestionsDE, merge_lists(suggestionsGB, suggestionsUS))

if __name__ == '__main__':
    print list_suggestions('tabaco')
    print list_suggetionsDE('Velo')