# -*- coding: utf-8 -*-
'''
Created on 25.10.2014

@author: Simon Gwerder
'''

from utilities.configloader import ConfigLoader
from utilities.retry import retry

import requests
from taginfostats import TagInfoStats

class TagInfo:

    cl = ConfigLoader()
    tagInfoSortDesc = cl.getTagInfoAPIString('SORT_DESC')

    tagInfoAllKeys = cl.getTagInfoAPIString('ALL_KEYS')
    tagInfoKeyStats = cl.getTagInfoAPIString('KEY_STATS')
    tagInfoTagStats = cl.getTagInfoAPIString('TAG_STATS')

    tagInfoValueOfKey = cl.getTagInfoAPIString('VALUE_OF_KEY')

    tagInfoWikiPageOfKey = cl.getTagInfoAPIString('WIKI_PAGE_OF_KEY')
    tagInfoWikiPageOfTag = cl.getTagInfoAPIString('WIKI_PAGE_OF_TAG')
    tagInfoTagPostfix = cl.getTagInfoAPIString('TAG_SUFFIX')

    @retry(Exception, tries=3)
    def getAllKeyData(self):
        '''Calls TagInfo for a list of all keys. The list is descending sorted by count of
           values attached to the key.'''
        keyResult = requests.get(self.tagInfoAllKeys + self.tagInfoSortDesc)
        keyJson = keyResult.json()
        return keyJson['data']

    @retry(Exception, tries=3)
    def getAllTagData(self, key):
        '''Calls TagInfo for a list of all tags for 'key'. The list is descending sorted by count of
        occurrence in OSM.'''
        tagResult = requests.get(self.tagInfoValueOfKey + key + self.tagInfoSortDesc)
        tagJson = tagResult.json()
        return tagJson['data']

    @retry(Exception, tries=3)
    def getKeyStats(self, key):
        '''Calls TagInfo for statistics of 'key'.'''
        keyResult = requests.get(self.tagInfoKeyStats + key)
        keyJson = keyResult.json();
        return keyJson['data']

    @retry(Exception, tries=3)
    def getTagStats(self, key, value):
        '''Calls TagInfo for statistics of 'key'='value'.'''
        tagResult = requests.get(self.tagInfoTagStats + key + self.tagInfoTagPostfix + value)
        tagJson = tagResult.json();
        return tagJson['data']

    @retry(Exception, tries=3)
    def getWikiPageOfKey(self, key):
        '''Calls TagInfo for the corresponding OSM wiki page for 'key'.'''
        keyWikiPage = requests.get(self.tagInfoWikiPageOfKey + key)
        return keyWikiPage.json()

    @retry(Exception, tries=3)
    def getWikiPageOfTag(self, key, value):
        '''Calls TagInfo for the corresponding OSM wiki page for 'key'='value'.'''
        tagWikiPage = requests.get(self.tagInfoWikiPageOfTag + key + self.tagInfoTagPostfix + value)
        return tagWikiPage.json()

    @retry(Exception, tries=3)
    def checkConnection(self):
        response = requests.get(self.tagInfoWikiPageOfTag + 'building' + self.tagInfoTagPostfix + 'yes')
        if response is not None and response.status_code < 400:
            return True
        return False

    def getTagInfoStats(self, key, value=None, wikiPageJson=None):
        '''Get the TagInfoStats object for further call methods'''
        return TagInfoStats(tagInfo = self, key=key, value=value, wikiPageJson=wikiPageJson)

if __name__ == '__main__':
    ti = TagInfo()
    print str(ti.checkConnection())
    statsJson = ti.getKeyStats('amenity')
    print str(statsJson)



