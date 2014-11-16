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

    def buildOSMLinksDictList(self, listOSMLinks):
        retList = []
        keyBaseLink = self.cl.getThesaurusString('KEY_SCHEME_NAME') + ':' # http://wiki.openstreetmap.org/wiki/Key:
        tagBaseLink = self.cl.getThesaurusString('TAG_SCHEME_NAME') + ':' # http://wiki.openstreetmap.org/wiki/Tag:
        for linkOrLabel in listOSMLinks:
            retDict = {}
            if 'http://' in linkOrLabel: # linkOrLabel is a link / concept
                if '=' in linkOrLabel: # represents a tag not a key
                    retDict['label']=linkOrLabel.replace(tagBaseLink, '')
                else: # represents a key
                    retDict['label']=linkOrLabel.replace(keyBaseLink, '') + '=' + '*' #utils.getAsteriskSymbol()
                retDict['link']=linkOrLabel
            else:
                if '=' in linkOrLabel: # represents a tag not a key
                    retDict['label']=linkOrLabel # linkOrLabel is a label (key or tag)
                else: # represents a key
                    retDict['label']=linkOrLabel + '=' + '*' #utils.getAsteriskSymbol()
                retDict['link']=None
            retList.append(retDict)
        return retList



    def fillResultList(self, rdfGraph, rawResults):
        for subject in rawResults:
            tag = {}

            prefLabelGen = rdfGraph.getPrefLabel(subject)
            broaderGen = rdfGraph.getBroader(subject)
            narrowerGen = rdfGraph.getNarrower(subject)
            scopeNoteGen = rdfGraph.getScopeNote(subject)
            depictionGen = rdfGraph.getDepiction(subject)
            osmNodeGen = rdfGraph.getOSMNode(subject)
            osmWayGen = rdfGraph.getOSMWay(subject)
            osmAreaGen = rdfGraph.getOSMArea(subject)
            osmRelationGen = rdfGraph.getOSMRelation(subject)
            osmImpliesGen = rdfGraph.getOSMImplies(subject)
            osmCombinesGen = rdfGraph.getOSMCombines(subject)
            osmLinksGen = rdfGraph.getOSMLinks(subject)

            default = { 'count' : '0', 'use' : 'False' }

            tag['subject'] = str(subject)

            tag['isKey'] = rdfGraph.isOSMKey(subject)
            tag['isTag'] = rdfGraph.isOSMTag(subject)

            tag['prefLabel'] = utils.genGetFirstItem(prefLabelGen)
            tag['broader']   = utils.genToList(broaderGen)
            tag['narrower'] = utils.genToList(narrowerGen)
            tag['scopeNote'] = utils.genToLangDict(scopeNoteGen)
            tag['depiction'] = utils.genGetFirstItem(depictionGen)

            tag['node']= utils.genJsonToDict(osmNodeGen, default)
            tag['way'] = utils.genJsonToDict(osmWayGen, default)
            tag['area'] = utils.genJsonToDict(osmAreaGen, default)
            tag['relation'] = utils.genJsonToDict(osmRelationGen, default)

            tag['implies'] = self.buildOSMLinksDictList( utils.genToList(osmImpliesGen) )
            tag['combines'] = self.buildOSMLinksDictList( utils.genToList(osmCombinesGen) )
            tag['links'] = self.buildOSMLinksDictList( utils.genToList(osmLinksGen) )

            tag['countAll'] = str(int(tag['node']['count']) + int(tag['way']['count']) + int(tag['relation']['count']) + int(tag['area']['count']))

            self.results.append(tag)



