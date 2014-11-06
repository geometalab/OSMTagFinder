# -*- coding: utf-8 -*-
'''
Created on 20.10.2014

@author: Simon Gwerder
'''

from rdflib import Literal

from utilities.configloader import ConfigLoader


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

    def genToList(self, generator):
        retList = []
        for item in generator:
            retList.append(str(item))
        return retList

    def genToLangDict(self, generator):
        retDict = {}
        for item in generator:
            print item
            print item.language
            retDict[item.language] = item
        return retDict;

    def genGetFirstItem(self, generator):
        try:
            firstItem = generator.next()
        except StopIteration:
            return None
        return str(firstItem)

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
            osmRelationGen = rdfGraph.getOSMRelation(subject)

            tag['subject'] = str(subject)

            tag['isKey'] = self.isKey(rdfGraph, subject)
            tag['isTag'] = self.isTag(rdfGraph, subject)

            tag['prefLabel'] = self.genGetFirstItem(prefLabelGen)
            tag['broader']   = self.genToList(broaderGen)
            tag['narrower'] = self.genToList(narrowerGen)
            tag['scopeNote'] = self.genToLangDict(scopeNoteGen)
            tag['depiction'] = self.genGetFirstItem(depictionGen)
            tag['countNodes']= self.genGetFirstItem(osmNodeGen)
            tag['countWays'] = self.genGetFirstItem(osmWayGen)
            tag['countRelations'] = self.genGetFirstItem(osmRelationGen)
            tag['countAll'] = str(int(tag['countNodes']) + int(tag['countWays']) + int(tag['countRelations']))

            self.results.append(tag)



