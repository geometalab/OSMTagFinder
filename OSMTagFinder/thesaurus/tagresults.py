# -*- coding: utf-8 -*-
'''
Created on 20.10.2014

@author: Simon Gwerder
'''

from utilities.configloader import ConfigLoader
from taginfo import TagInfo

class TagResults:

    cl = ConfigLoader()
    tagInfo = TagInfo()
    results = []

    def __init__(self, rdfGraph, rawResults):
        self.results = []
        self.fillResultList(rdfGraph, rawResults)
        self.results = sorted(self.results, reverse=True, key=self.sortKey)

    def getResults(self):
        return self.results

    def sortKey(self, tag):
        return int(tag['countAll'])


    def isKey(self, rdfGraph, subject):
        keyScheme = self.cl.getThesaurusString('KEY_SCHEME_NAME')
        return rdfGraph.isInScheme(subject, keyScheme)

    def isTag(self, rdfGraph, subject):
        tagScheme = self.cl.getThesaurusString('TAG_SCHEME_NAME')
        return rdfGraph.isInScheme(subject, tagScheme)

    def genToList(self, generator):
        retList = []
        for item in generator:
            retList.append(str(item))
        return retList

    def genGetFirstItem(self, generator):
        try:
            firstItem = generator.next()
        except StopIteration:
            return None
        return str(firstItem)

    def getStatsData(self, tagInfos):
        statsData = {}
        if tagInfos['isKey']:
            statsData = self.tagInfo.getKeyStats(tagInfos['prefLabel'])
        else:
            prefLabel = tagInfos['prefLabel']
            key = prefLabel.split('=')[0]
            value = prefLabel.split('=')[1]
            statsData = self.tagInfo.getTagStats(key, value)
        return statsData

    def getCountAll(self, statsData):
        for item in statsData:
            if item['type'] == 'all':
                return item['count']
        return '0'

    def getCountNodes(self, statsData):
        for item in statsData:
            if item['type'] == 'nodes':
                return item['count']
        return '0'

    def getCountWays(self, statsData):
        for item in statsData:
            if item['type'] == 'ways':
                return item['count']
        return '0'

    def getCountRelations(self, statsData):
        for item in statsData:
            if item['type'] == 'relations':
                return item['count']
        return '0'

    def fillResultList(self, rdfGraph, rawResults):
        for subject in rawResults:
            tag = {}

            prefLabelGen = rdfGraph.getPrefLabels(subject)
            broaderGen = rdfGraph.getBroader(subject)
            narrowerGen = rdfGraph.getNarrower(subject)
            scopeNoteGen = rdfGraph.getScopeNote(subject)
            depictionGen = rdfGraph.getDepiction(subject)

            tag['subject'] = str(subject)

            tag['isKey'] = self.isKey(rdfGraph, subject)
            tag['isTag'] = self.isTag(rdfGraph, subject)

            tag['prefLabel'] = self.genGetFirstItem(prefLabelGen)
            tag['broader']   = self.genToList(broaderGen)
            tag['narrower'] = self.genToList(narrowerGen)
            tag['broader'] = self.genToList(broaderGen)
            tag['scopeNote'] = self.genToList(scopeNoteGen)
            tag['depiction'] = self.genGetFirstItem(depictionGen)

            statsData = self.getStatsData(tag)

            tag['countAll'] = self.getCountAll(statsData)
            tag['countNodes']= self.getCountAll(statsData)
            tag['countWays'] = self.getCountAll(statsData)
            tag['countRelations'] = self.getCountAll(statsData)

            self.results.append(tag)



