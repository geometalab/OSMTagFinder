# -*- coding: utf-8 -*-
'''
Created on 25.10.2014

@author: Simon Gwerder
'''

from utilities.configloader import ConfigLoader
import requests

class TagInfo:

    cl = ConfigLoader()
    tagInfoSortDesc = cl.getTagInfoAPIString('SORT_DESC')

    tagInfoAllKeys = cl.getTagInfoAPIString('ALL_KEYS')
    tagInfoKeyStats = cl.getTagInfoAPIString('KEY_STATS')

    tagInfoValueOfKey = cl.getTagInfoAPIString('VALUE_OF_KEY')

    tagInfoWikiPageOfKey = cl.getTagInfoAPIString('WIKI_PAGE_OF_KEY')
    tagInfoWikiPageOfTag = cl.getTagInfoAPIString('WIKI_PAGE_OF_TAG')
    tagInfoTagPostfix = cl.getTagInfoAPIString('TAG_SUFFIX')


    def getListOfValidKeys(self, minCount):
        '''Calls TagInfo for a list of all keys. The elements in the list are then checked for their validity.
        'minCount' is a restriction on the number of occurence of a key and the number of values per key.
        The returned list is descending sorted by count of values attached to the key.'''
        keyData = self.tagInfo.getAllKeyData()
        return self.filterKeyData(keyData, minCount)

    def getAllKeyData(self):
        '''Calls TagInfo for a list of all keys. The list is descending sorted by count of
           values attached to the key.'''
        keyResult = requests.get(self.tagInfoAllKeys + self.tagInfoSortDesc)
        keyJson = keyResult.json()
        return keyJson['data']

    def getAllTagData(self, key):
        '''Calls TagInfo for a list of all tags for 'key'. The list is descending sorted by count of
        occurrence in OSM.'''
        tagResult = requests.get(self.tagInfoValueOfKey + key + self.tagInfoSortDesc)
        tagJson = tagResult.json()
        return tagJson['data']

    def getKeyStats(self, key):
        '''Calls TagInfo for statistics of 'key'.'''
        keyResult = requests.get(self.tagInfoKeyStats + key)
        keyJson = keyResult.json();
        return keyJson['data']

    def getTagStats(self, key, value):
        '''Calls TagInfo for statistics of 'key'='value'.'''
        tagResult = requests.get(self.tagInfoKeyStats + key + self.tagInfoTagPostfix + value)
        tagJson = tagResult.json();
        return tagJson['data']

    def getWikiPageOfKey(self, key):
        '''Calls TagInfo for the corresponding OSM wiki page for 'key'.'''
        keyWikiPage = requests.get(self.tagInfoWikiPageOfKey + key)
        return keyWikiPage.json()

    def getWikiPageOfTag(self, key, value):
        '''Calls TagInfo for the corresponding OSM wiki page for 'key'='value'.'''
        tagWikiPage = requests.get(self.tagInfoWikiPageOfTag + key + self.tagInfoTagPostfix + value)
        return tagWikiPage.json()


if __name__ == '__main__':
    ti = TagInfo()
    statsJson = ti.getKeyStats('amenity')
    print str(statsJson['all'])


