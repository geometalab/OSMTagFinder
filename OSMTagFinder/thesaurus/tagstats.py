# -*- coding: utf-8 -*-
'''
Created on 30.10.2014

@author: Simon Gwerder
'''

from taginfo import TagInfo

class TagStats:

    tagInfo = TagInfo()

    statsData = None

    def __init__(self, key, value=None):
        self.statsData = self.getStatsData(key, value)

    def getStatsData(self, key, value=None):
        if value is None:
            return self.tagInfo.getKeyStats(key)
        else:
            return self.tagInfo.getTagStats(key, value)

    def getCountAll(self):
        '''Returns the total count of this osm key or tag as string'''
        for item in self.statsData:
            if item['type'] == 'all':
                return item['count']
        return '0'

    def getCountNodes(self):
        '''Returns the node count of this osm key or tag as string'''
        for item in self.statsData:
            if item['type'] == 'nodes':
                return item['count']
        return '0'

    def getCountWays(self):
        '''Returns the way count of this osm key or tag as string'''
        for item in self.statsData:
            if item['type'] == 'ways':
                return item['count']
        return '0'

    def getCountRelations(self):
        '''Returns the relation count of this osm key or tag as string'''
        for item in self.statsData:
            if item['type'] == 'relations':
                return item['count']
        return '0'

if __name__ == '__main__':
    tagStats = TagStats('building','yes')
    print tagStats.getCountAll()
    print tagStats.getCountNodes()
    print tagStats.getCountWays()
    print tagStats.getCountRelations()
