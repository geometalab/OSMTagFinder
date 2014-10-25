# -*- coding: utf-8 -*-
'''
Created on 20.10.2014

@author: Simon Gwerder
'''

from utilities.configloader import ConfigLoader

class TagResults:

    cl = ConfigLoader()
    results = []

    def __init__(self, rdfGraph, rawResults):
        self.results = []
        self.getTagInformation(rdfGraph, rawResults)

    def getResults(self):
        return self.results

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

    def getTagInformation(self, rdfGraph, rawResults):
        for subject in rawResults:
            tagInfos = {}

            prefLabelGen = rdfGraph.getPrefLabels(subject)
            broaderGen = rdfGraph.getBroader(subject)
            narrowerGen = rdfGraph.getNarrower(subject)
            scopeNoteGen = rdfGraph.getScopeNote(subject)
            depictionGen = rdfGraph.getDepiction(subject)

            tagInfos['subject'] = str(subject)
            tagInfos['isKey'] = self.isKey(rdfGraph, subject)
            tagInfos['isTag'] = self.isTag(rdfGraph, subject)
            tagInfos['prefLabel'] = self.genGetFirstItem(prefLabelGen)
            tagInfos['broader'] = self.genToList(broaderGen)
            tagInfos['narrower'] = self.genToList(narrowerGen)
            tagInfos['broader'] = self.genToList(broaderGen)
            tagInfos['scopeNote'] = self.genToList(scopeNoteGen)
            tagInfos['depiction'] = self.genGetFirstItem(depictionGen)

            self.results.append(tagInfos)

