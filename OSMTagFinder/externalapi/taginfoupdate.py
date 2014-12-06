# -*- coding: utf-8 -*-
'''
Created on 30.10.2014

@author: Simon Gwerder
'''

from externalapi.taginfo import TagInfo

class TagInfoUpdate:

    tagInfo = TagInfo()

    statsData = None
    wikiPageJson = None

    def __init__(self, key, value=None, wikiPageJson=None):
        self.getData(key, value, wikiPageJson)


    def getData(self, key, value=None, wikiPageJson=None):
        if value is None:
            self.statsData = self.tagInfo.getKeyStats(key)
            if wikiPageJson is None:
                wikiPageJson = self.tagInfo.getWikiPageOfKey(key)
            self.wikiPageJson = wikiPageJson
        else:
            self.statsData = self.tagInfo.getTagStats(key, value)
            if wikiPageJson is None:
                wikiPageJson = self.tagInfo.getWikiPageOfTag(key, value)
            self.wikiPageJson = wikiPageJson

    def getOnNode(self):
        '''Returns boolean whether this osm key or tag is used on nodes.'''
        for wikiData in self.wikiPageJson:
            if wikiData['lang'] == 'en':
                return wikiData['on_node']
        return False

    def getOnWay(self):
        '''Returns boolean whether this osm key or tag is used on ways.'''
        for wikiData in self.wikiPageJson:
            if wikiData['lang'] == 'en':
                return wikiData['on_way']
        return False

    def getOnArea(self):
        '''Returns boolean whether this osm key or tag is used on areas.'''
        for wikiData in self.wikiPageJson:
            if wikiData['lang'] == 'en':
                return wikiData['on_area']
        return False

    def getOnRelation(self):
        '''Returns boolean whether this osm key or tag is used on relations.'''
        for wikiData in self.wikiPageJson:
            if wikiData['lang'] == 'en':
                return wikiData['on_relation']
        return False


    def getCountAll(self):
        '''Returns the total count of this osm key or tag as string.'''
        for item in self.statsData:
            if item['type'] == 'all':
                return item['count']
        return '0'

    def getCountNodes(self):
        '''Returns the node count of this osm key or tag as string.'''
        for item in self.statsData:
            if item['type'] == 'nodes':
                return item['count']
        return '0'

    def getCountWays(self):
        '''Returns the way count of this osm key or tag as string.'''
        for item in self.statsData:
            if item['type'] == 'ways':
                return item['count']
        return '0'

    def getCountRelations(self):
        '''Returns the relation count of this osm key or tag as string.'''
        for item in self.statsData:
            if item['type'] == 'relations':
                return item['count']
        return '0'

    def getListImplies(self):
        '''Returns a array of strings of tags that this tag 'implies'. '''
        for wikiData in self.wikiPageJson:
            if wikiData['lang'] == 'en':
                return wikiData['tags_implies']
        return []

    def getListCombinations(self):
        '''Returns a array of strings of tags that are often 'combined' with this tag.'''
        for wikiData in self.wikiPageJson:
            if wikiData['lang'] == 'en':
                return wikiData['tags_combination']
        return []

    def getListLinked(self):
        '''Returns a array of strings of tags that are 'linked' to this tag.'''
        for wikiData in self.wikiPageJson:
            if wikiData['lang'] == 'en':
                return wikiData['tags_linked']
        return []


if __name__ == '__main__':
    tagInfoUpdate = TagInfoUpdate('tourism','hotel')
    print tagInfoUpdate.getCountAll()
    print tagInfoUpdate.getCountNodes()
    print tagInfoUpdate.getCountWays()
    print tagInfoUpdate.getCountRelations()

    print tagInfoUpdate.getOnNode()
    print tagInfoUpdate.getOnWay()
    print tagInfoUpdate.getOnArea()
    print tagInfoUpdate.getOnRelation()

