# -*- coding: utf-8 -*-
'''
Created on 20.10.2014

@author: Simon Gwerder
'''

from utilities.configloader import ConfigLoader
from utilities import utils


class TagResults:

    cl = ConfigLoader()
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



    def fillResultList(self, rdfGraph, rawResults):
        for subject in rawResults:
            tag = {}

            prefLabelGen = rdfGraph.getPrefLabels(subject)
            broaderGen = rdfGraph.getBroader(subject)
            narrowerGen = rdfGraph.getNarrower(subject)
            scopeNoteGen = rdfGraph.getScopeNote(subject)
            depictionGen = rdfGraph.getDepiction(subject)
            osmNodeGen = rdfGraph.getOSMNode(subject)
            osmWayGen = rdfGraph.getOSMWay(subject)
            osmAreaGen = rdfGraph.getOSMArea(subject)
            osmRelationGen = rdfGraph.getOSMRelation(subject)
            default = { 'count' : '0', 'use' : 'false' }

            tag['subject'] = str(subject)

            tag['isKey'] = self.isKey(rdfGraph, subject)
            tag['isTag'] = self.isTag(rdfGraph, subject)

            tag['prefLabel'] = utils.genGetFirstItem(prefLabelGen)
            tag['broader']   = utils.genToList(broaderGen)
            tag['narrower'] = utils.genToList(narrowerGen)
            tag['scopeNote'] = utils.genToLangDict(scopeNoteGen)
            tag['depiction'] = utils.genGetFirstItem(depictionGen)
            tag['node']= utils.genJsonToDict(osmNodeGen, default)
            tag['way'] = utils.genJsonToDict(osmWayGen, default)
            tag['area'] = utils.genJsonToDict(osmAreaGen, default)
            tag['relation'] = utils.genJsonToDict(osmRelationGen, default)
            tag['countAll'] = str(int(tag['node']['count']) + int(tag['way']['count']) + int(tag['relation']['count']) + int(tag['area']['count']))

            self.results.append(tag)



