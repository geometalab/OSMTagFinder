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
        #self.results = sorted(self.results, reverse=True, key=self.sortKey)
        self.results = self.sortResults(self.results) # sorting by section


    def getResults(self):
        return self.results

    def sortKey(self, tag):
        return int(tag['countAll'])

    def sortResults(self, unsortedResults):

        byTagPrefLabel = []
        byTermPrefLabel = []
        byTermAltLabel = []
        byTermBroader = []
        byTermNarrower = []
        byTagScopeNote = []

        sortedResults = []

        for result in unsortedResults:

            if not 'searchMeta' in result: return unsortedResults

            searchMeta = result['searchMeta']

            hasTermBroader = 'termBroader' in searchMeta
            hasTermNarrower = 'termNarrower' in searchMeta
            hasTagPrefLabel = 'tagPrefLabel' in searchMeta
            hasTermPrefLabel = 'termPrefLabel' in searchMeta
            hasTermAltLabel = 'termAltLabel' in searchMeta
            hasTagScopeNote = 'tagScopeNote' in searchMeta

            if hasTermBroader and not hasTagPrefLabel and not hasTermPrefLabel and not hasTermAltLabel:
                byTermBroader.append(result)
                continue
            if hasTermNarrower and not hasTagPrefLabel and not hasTermPrefLabel and not hasTermAltLabel:
                byTermNarrower.append(result)
                continue
            if hasTagPrefLabel:
                byTagPrefLabel.append(result)
                continue
            if hasTermPrefLabel:
                byTermPrefLabel.append(result)
                continue
            if  hasTermAltLabel:
                byTermAltLabel.append(result)
                continue
            if hasTagScopeNote:
                byTagScopeNote.append(result)
                continue

        sortedResults.extend( sorted(byTagPrefLabel, reverse=True, key=self.sortKey) )
        sortedResults.extend( sorted(byTermPrefLabel, reverse=True, key=self.sortKey) )
        sortedResults.extend( sorted(byTermAltLabel, reverse=True, key=self.sortKey) )
        sortedResults.extend( sorted(byTermBroader, reverse=True, key=self.sortKey) )
        sortedResults.extend( sorted(byTermNarrower, reverse=True, key=self.sortKey) )
        sortedResults.extend( sorted(byTagScopeNote, reverse=True, key=self.sortKey) )

        return sortedResults


    def buildOSMLinksListDict(self, listOSMLinks):
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

    def buildRelTermsDictList(self, rdfGraph, listRelatedMatches):
        relatedTerms = { }
        relatedTerms['en'] = []
        relatedTerms['de'] = []
        for relMatchSubject in listRelatedMatches:
            if rdfGraph.isInTermScheme(relMatchSubject):
                termAltLabelGen = rdfGraph.getAltLabel(relMatchSubject)
                for termAltLabel in termAltLabelGen:
                    if not hasattr(termAltLabel, 'language'): continue # is not Literal in that case
                    if termAltLabel.language == 'en' or termAltLabel.language == 'de':
                        listTerms = relatedTerms[str(termAltLabel.language)]
                        listTerms.append(utils.encode(termAltLabel))
                        relatedTerms[str(termAltLabel.language)] = listTerms
                termPrefLabelGen = rdfGraph.getPrefLabel(relMatchSubject)
                for termPrefLabel in termPrefLabelGen:
                    if not hasattr(termPrefLabel, 'language'): continue # is not Literal in that case
                    if termPrefLabel.language == 'en' or termPrefLabel.language == 'de':
                        listTerms = relatedTerms[str(termPrefLabel.language)]
                        listTerms.insert(0, termPrefLabel)
                        relatedTerms[str(termPrefLabel.language)] = listTerms
        return relatedTerms



    def fillResultList(self, rdfGraph, rawResults):
        for subject in rawResults:
            tag = { }

            searchMeta = rawResults[subject]

            prefLabelGen = rdfGraph.getPrefLabel(subject)
            #broaderGen = rdfGraph.getBroader(subject)
            #narrowerGen = rdfGraph.getNarrower(subject)
            scopeNoteGen = rdfGraph.getScopeNote(subject)
            depictionGen = rdfGraph.getDepiction(subject)
            osmNodeGen = rdfGraph.getOSMNode(subject)
            osmWayGen = rdfGraph.getOSMWay(subject)
            osmAreaGen = rdfGraph.getOSMArea(subject)
            osmRelationGen = rdfGraph.getOSMRelation(subject)
            osmImpliesGen = rdfGraph.getOSMImplies(subject)
            osmCombinesGen = rdfGraph.getOSMCombines(subject)
            osmLinksGen = rdfGraph.getOSMLinks(subject)

            relatedMatchGen = rdfGraph.getRelatedMatch(subject)

            default = { 'count' : '0', 'use' : 'False' }

            tag['subject'] = utils.encode(subject)

            if searchMeta is not None and len(searchMeta) > 0:
                tag['searchMeta'] = searchMeta

            tag['isKey'] = rdfGraph.isInKeyScheme(subject)
            tag['isTag'] = rdfGraph.isInTagScheme(subject)

            tag['prefLabel'] = utils.genGetFirstItem(prefLabelGen)
            #tag['broader']   = utils.genToList(broaderGen)
            #tag['narrower'] = utils.genToList(narrowerGen)
            tag['scopeNote'] = utils.genToLangDict(scopeNoteGen)
            tag['depiction'] = utils.genGetFirstItem(depictionGen)

            tag['node']= utils.genJsonToDict(osmNodeGen, default)
            tag['way'] = utils.genJsonToDict(osmWayGen, default)
            tag['area'] = utils.genJsonToDict(osmAreaGen, default)
            tag['relation'] = utils.genJsonToDict(osmRelationGen, default)

            tag['implies'] = self.buildOSMLinksListDict( utils.genToList(osmImpliesGen) )
            tag['combines'] = self.buildOSMLinksListDict( utils.genToList(osmCombinesGen) )
            tag['links'] = self.buildOSMLinksListDict( utils.genToList(osmLinksGen) )

            tag['countAll'] = int(tag['node']['count']) + int(tag['way']['count']) + int(tag['relation']['count']) + int(tag['area']['count'])

            tag['termRelated'] = self.buildRelTermsDictList( rdfGraph, utils.genToList(relatedMatchGen) )

            self.results.append(tag)



