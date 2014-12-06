# -*- coding: utf-8 -*-
'''
Created on 27.09.2014

@author: Simon Gwerder
'''

from filter import Filter
from utilities import utils
from utilities.configloader import ConfigLoader
from thesaurus.rdfgraph import RDFGraph
from externalapi.taginfo import TagInfo
from externalapi.taginfoupdate import TagInfoUpdate
from utilities.translator import Translator
from thesaurus.mapsemnet import MapOSMSemanticNet

class BaseThesaurus:

    rdfGraph = RDFGraph()
    tagInfo = TagInfo()
    numberKeys = 0
    numberTags = 0

    cl = ConfigLoader()

    osmWikiBase = cl.getThesaurusString('OSM_WIKI_PAGE')
    keySchemeName = cl.getThesaurusString('KEY_SCHEME_NAME')
    tagSchemeName = cl.getThesaurusString('TAG_SCHEME_NAME')
    keySchemeTitle = cl.getThesaurusString('KEY_SCHEME_TITLE')
    tagSchemeTitle = cl.getThesaurusString('TAG_SCHEME_TITLE')
    creator = cl.getThesaurusString('CREATOR')

    outputName = cl.getThesaurusString('OUTPUT_NAME')  # tagfinder_thesaurus
    outputEnding = cl.getThesaurusString('DEFAULT_FORMAT')  # .rdf

    translationHintDE = cl.getThesaurusString('TRANSLATION_HINT_DE')
    translationHintEN = cl.getThesaurusString('TRANSLATION_HINT_EN')
    editNote = cl.getThesaurusString('NO_TERM')

    valueMinCount = cl.getThesaurusInt('MINIMUM_COUNT')

    filterUtil = Filter()
    translator = Translator()

    console = None

    def __init__(self, rdfGraph=None, console=None):
        if rdfGraph is not None:
            self.rdfGraph = rdfGraph
        if console is not None:
            self.console = console

    def createBaseThesaurus(self, console):
        if console is not None:
            self.console = console

        self.printMessage(' Requesting valid OSM keys from "' + self.cl.getTagInfoAPIString('TAGINFO_PAGE')  + '":')
        keyList = self.getListOfValidKeys()

        self.numberKeys = len(keyList) + len(self.filterUtil.exactKeyFilter)
        self.printMessage(' Got ' + str(len(keyList)) + ' valid OSM keys. ' + str(len(self.filterUtil.exactKeyFilter)) + ' are additional keys from filter.')

        self.printMessage('\n Requesting valid OSM tags from "' + self.cl.getTagInfoAPIString('TAGINFO_PAGE')  + '":')
        tagMap = self.bundleToTagMap(keyList)

        self.numberTags = self.numberTags(tagMap)
        self.printMessage(' Got ' + str(self.numberTags) + ' valid OSM tags.')

        empty = []
        for filteredKey in self.filterUtil.exactKeyFilter:
            tagMap[filteredKey] = empty

        self.printMessage('\n Requesting detailed information from "' + self.cl.getTagInfoAPIString('TAGINFO_PAGE')  + '":')
        self.createGraph(keyList, tagMap)

        self.printMessage('\n Linking OSM "implies", "combines" and "links" relations to graph concepts')
        self.osmLinksToConcept()

        self.printMessage('\n Create mapping to OSM Semantic Net')
        osnSemNetFilePath = utils.semnetDir() + 'osm_semantic_network.rdf'
        MapOSMSemanticNet(self.rdfGraph, osnSemNetFilePath)

        fullPath = utils.outputFile(utils.tempDir(), self.outputName, self.outputEnding, useDateEnding=True)
        name = fullPath[fullPath.rfind('\\') + 1:]
        self.printMessage('\n Serializing graph to: ' + name)
        self.rdfGraph.serialize(fullPath)
        self.printMessage('\n Finished creating TagFinder BaseThesaurus')

    def printPercent(self, partInt, totalInt, workingOn=None):
        '''Only print percents if according outwriter was defined'''
        if self.console is not None:
            self.console.printPercent(partInt, totalInt, workingOn)

    def printMessage(self, message):
        '''Only print message if according outwriter was defined'''
        if self.console is not None:
            self.console.println(message)

    def numberTags(self, tagMap):
        '''Returns number of tags in 'tagMap'.'''
        count = 0
        for key in tagMap:
            listValues = tagMap[key]
            count = count + len(listValues)
        return count

    def getBaseGraph(self):
        '''Getter for the base rdfGraph.'''
        return self.rdfGraph

    def getListOfValidKeys(self):
        '''Calls TagInfo for a list of all keys. The elements in the list are then checked for their validity.
        'minCount' is a restriction on the number of occurence of a key and the number of values per key.
        The returned list is descending sorted by count of values attached to the key.'''
        keyData = self.tagInfo.getAllKeyData()
        return self.filterKeyData(keyData)

    def filterKeyData(self, keyData):
        '''Takes the raw key data from 'keyData' and makes validation checks on each
           element. Then a list of valid keys is returned.'''
        keyList = []
        atPart = 1
        for keyItem in keyData:
            #if keyItem['count_all'] < self.valueMinCount:
                #break;  # speedup because of sorted list
            if not self.filterUtil.hasKey(keyItem['key']) and utils.validCharsCheck(keyItem['key']) and keyItem['values_all'] >= self.valueMinCount:
                keyList.append(keyItem['key'])
                self.printPercent(partInt=atPart, totalInt=len(keyData), workingOn='Getting key: ' + keyItem['key'])
            atPart = atPart + 1
        self.printPercent(partInt=1, totalInt=1)

        return keyList

    def filterTagData(self, key, tagMap, tagData):
        '''Takes the raw key data from 'tagData' and makes validation checks on each
           element. Then the updated 'tagMap' (k:key, v:value) is returned.'''
        for valueItem in tagData:
            if not self.filterUtil.hasValue(valueItem['value']) and valueItem['in_wiki'] and utils.validCharsCheck(valueItem['value']) and valueItem['count'] >= self.valueMinCount:
                k = tagMap.get(key)
                if k is not None:
                    k.append(valueItem['value'])
                else:
                    k = [valueItem['value']]
                tagMap[key] = k
        return tagMap

    def bundleToTagMap(self, keyList):
        '''Creates a hash map with k:key and v:value of valid keys and values.'''
        tagMap = {}
        atPart = 1
        for key in keyList:
            self.printPercent(atPart, len(keyList), 'Getting all tags for key: ' + key)
            tagData = self.tagInfo.getAllTagData(key)
            tagMap = self.filterTagData(key, tagMap, tagData)
            atPart = atPart + 1
        return tagMap

    def addDepictionScopeNote(self, concept, wikiPageJson, new=True):
        '''Adds a depiction and scopeNote in EN and DE to the 'concept' (if available,
           also translates to the other language if only one is).'''
        scopeNoteDE = ''
        scopeNoteEN = ''
        depiction = ''

        for wikiData in wikiPageJson:

            if wikiData['lang'] == 'de':
                temp = wikiData['description']
                if temp is not None and not temp == '':
                    temp = temp.replace('\'', '')
                    temp = temp.replace('[[w:','')
                    temp = temp.replace('[[w', '')
                    temp = temp.replace('[[de:','')
                    temp = temp.replace('[[en:','')
                    temp = temp.replace('en=','')
                    temp = temp.replace('[[wikipedia:de:', '')
                    temp = temp.replace('[[wikipedia:en:', '')
                    temp = temp.replace('[[wikipedia:','')
                    temp = temp.replace('[[Wikipedia:','')
                    temp = temp.replace('[[wiktionary:de:', '')
                    temp = temp.replace('[[wiktionary:en:', '')
                    temp = temp.replace('[[Wiktionary:','')
                    temp = temp.replace('[[wiktionary:','')
                    temp = temp.replace('[[','')
                    temp = temp.replace(']]', '')
                    scopeNoteDE = temp
            elif wikiData['lang'] == 'en':
                temp = wikiData['description']
                if  temp is not None and not temp == '':
                    temp = temp.replace('\'', '')
                    scopeNoteEN = temp
                    imageData = wikiData['image']
                    depiction = imageData['image_url']
            if depiction is None or depiction == '':
                imageData = wikiData['image']
                depiction = imageData['image_url']

        if scopeNoteDE == '' and not scopeNoteEN == '':
            if new:
                self.rdfGraph.addScopeNote(concept, scopeNoteEN, 'en')
                self.rdfGraph.addScopeNote(concept, self.translator.translateENtoDE(scopeNoteEN) + ' ' + self.translationHintDE, 'de')
            else:
                self.rdfGraph.setScopeNote(concept, scopeNoteEN, 'en')
                self.rdfGraph.addScopeNote(concept, self.translator.translateENtoDE(scopeNoteEN) + ' ' + self.translationHintDE, 'de')
        elif not scopeNoteDE == '' and scopeNoteEN == '':
            if new:
                self.rdfGraph.addScopeNote(concept, self.translator.translateDEtoEN(scopeNoteDE) + ' ' + self.translationHintEN, 'en')
                self.rdfGraph.addScopeNote(concept, scopeNoteDE, 'de')
            else:
                self.rdfGraph.setScopeNote(concept, self.translator.translateDEtoEN(scopeNoteDE) + ' ' + self.translationHintEN, 'en')
                self.rdfGraph.addScopeNote(concept, scopeNoteDE, 'de')
        elif not scopeNoteDE == '' and not scopeNoteEN == '':
            if new:
                self.rdfGraph.addScopeNote(concept, scopeNoteEN, 'en')
                self.rdfGraph.addScopeNote(concept, scopeNoteDE, 'de')
            else:
                self.rdfGraph.setScopeNote(concept, scopeNoteEN, 'en')
                self.rdfGraph.addScopeNote(concept, scopeNoteDE, 'de')

        if depiction is not None and not depiction == '' and new:
            self.rdfGraph.addDepiction(concept, depiction)

        if depiction is not None and not depiction == '' and not new:
            self.rdfGraph.setDepiction(concept, depiction)

    def updateTagStats(self, concept, key, value=None, wikiPageJson=None, new=True):
        '''Updates stats counts, node use, way use, area use and relation use.'''
        tagInfoUpdate = TagInfoUpdate(key=key, value=value, wikiPageJson=wikiPageJson)

        nodeStr = '{ "count": "0", "use": "False" }' # dummy values
        wayStr = '{ "count": "0", "use": "False" }'
        areaStr = '{ "count": "0", "use": "False" }'
        relationStr = '{ "count": "0", "use": "False" }'

        if value is None:
            nodeStr = '{ "count": "' + str(tagInfoUpdate.getCountNodes()) + '", "use": "False" }'
            wayStr = '{ "count": "' + str(tagInfoUpdate.getCountWays()) + '", "use": "False" }'
            areaStr = '{ "count": "0", "use": "False" }'
            relationStr = '{ "count": "' + str(tagInfoUpdate.getCountRelations()) + '", "use": "False" }'
        else:
            onNode =  tagInfoUpdate.getOnNode()
            onWay = tagInfoUpdate.getOnWay()
            onRelation = tagInfoUpdate.getOnRelation()
            #if not onNode and not onWay and not onRelation:
            #    onArea = True
            #else:
            #    onArea = tagInfoUpdate.getOnArea()
            onArea = tagInfoUpdate.getOnArea()

            nodeStr = '{ "count": "' + str(tagInfoUpdate.getCountNodes()) + '", "use": "' + str(onNode) + '" }'
            wayStr = '{ "count": "' + str(tagInfoUpdate.getCountWays()) + '", "use": "' + str(onWay) + '" }'
            areaStr = '{ "count": "0"' + ', "use": "' + str(onArea) + '" }'
            relationStr = '{ "count": "' + str(tagInfoUpdate.getCountRelations()) + '", "use": "' + str(onRelation) + '" }'

        if new:
            self.rdfGraph.addOSMNode(concept, nodeStr)
            self.rdfGraph.addOSMWay(concept, wayStr)
            self.rdfGraph.addOSMArea(concept, areaStr)
            self.rdfGraph.addOSMRelation(concept, relationStr)
        else:
            self.rdfGraph.setOSMNode(concept, nodeStr)
            self.rdfGraph.setOSMWay(concept, wayStr)
            self.rdfGraph.setOSMArea(concept, areaStr)
            self.rdfGraph.setOSMRelation(concept, relationStr)

    def deleteAllLinks(self, concept):
        '''Deletes all link for 'concept', UriRefs and Literals.'''
        self.rdfGraph.setOSMImpliesUriRef(concept, 'dummy')
        self.rdfGraph.setOSMCombinesUriRef(concept, 'dummy')
        self.rdfGraph.setOSMLinksUriRef(concept, 'dummy')

        self.rdfGraph.setOSMImpliesLiteral(concept, 'dummy')
        self.rdfGraph.setOSMCombinesLiteral(concept, 'dummy')
        self.rdfGraph.setOSMLinksLiteral(concept, 'dummy')

        self.rdfGraph.removeOSMImpliesUriRef(concept, 'dummy')
        self.rdfGraph.removeOSMCombinesUriRef(concept, 'dummy')
        self.rdfGraph.removeOSMLinksUriRef(concept, 'dummy')

        self.rdfGraph.removeOSMImpliesLiteral(concept, 'dummy')
        self.rdfGraph.removeOSMCombinesLiteral(concept, 'dummy')
        self.rdfGraph.removeOSMLinksLiteral(concept, 'dummy')

    def updateTagLinks(self, concept, key, value=None, wikiPageJson=None, new=True):
        '''Updates the tag links from OSM wiki: implies, combinations and linked. Just as Literals.'''
        tagInfoUpdate = TagInfoUpdate(key=key, value=value, wikiPageJson=wikiPageJson)

        listImplies = tagInfoUpdate.getListImplies()
        listCombinations = tagInfoUpdate.getListCombinations()
        listLinked = tagInfoUpdate.getListLinked()

        if not new:
            self.deleteAllLinks(concept)

        impliesStr = '\t\tImplies: '
        for tagImplies in listImplies: #tags or keys
            self.rdfGraph.addOSMImpliesLiteral(concept, tagImplies)
            impliesStr = impliesStr + tagImplies + ', '

        combinesStr = '\t\tCombines: '
        for tagCombines in listCombinations: #tags or keys
            self.rdfGraph.addOSMCombinesLiteral(concept, tagCombines)
            combinesStr = combinesStr + tagCombines + ', '

        linksStr = '\t\tLinks: '
        for tagLinks in listLinked: #tags or keys
            self.rdfGraph.addOSMLinksLiteral(concept, tagLinks)
            linksStr = linksStr + tagLinks + ', '

    def createKey(self, key, keyScheme):
        '''Adds key with name 'key' to the rdfGraph, with as much wiki information as possible.'''
        keyConcept = self.rdfGraph.addConcept(self.osmWikiBase + 'Key:' + key)
        self.rdfGraph.addInScheme(keyConcept, keyScheme)
        self.rdfGraph.addPrefLabel(keyConcept, key)

        # rdfGraph.addHasTopConcept(keyScheme, keyConcept)

        keyWikiPageJson = self.tagInfo.getWikiPageOfKey(key)
        if len(keyWikiPageJson) > 0:
            self.updateTagStats(concept=keyConcept, key=key, wikiPageJson=keyWikiPageJson)
            self.updateTagLinks(concept=keyConcept, key=key, wikiPageJson=keyWikiPageJson)
            self.addDepictionScopeNote(keyConcept, keyWikiPageJson)

        self.rdfGraph.addEditorialNote(keyConcept, self.editNote)

        return keyConcept

    def createTag(self, key, keyConcept, value, tagScheme):
        '''Adds value with name 'key'='value' to the rdfGraph, with as much wiki information as possible.'''
        taglink = self.osmWikiBase + 'Tag:' + key + '=' + value  # before: key + '%3D' + value
        # result = requests.get('http://' + taglink)
        tagWikiPageJson = self.tagInfo.getWikiPageOfTag(key, value)
        if len(tagWikiPageJson) > 0:
            tagConcept = self.rdfGraph.addConcept(taglink)
            self.rdfGraph.addInScheme(tagConcept, tagScheme)
            self.rdfGraph.addPrefLabel(tagConcept, key + '=' + value)
            self.rdfGraph.addBroader(tagConcept, keyConcept)
            self.rdfGraph.addNarrower(keyConcept, tagConcept)

            self.updateTagStats(concept=tagConcept, key=key, value=value, wikiPageJson=tagWikiPageJson)
            self.updateTagLinks(concept=tagConcept, key=key, value=value, wikiPageJson=tagWikiPageJson)

            self.addDepictionScopeNote(tagConcept, tagWikiPageJson)

            self.rdfGraph.addEditorialNote(tagConcept, self.editNote)

            return tagConcept

    def createGraph(self, keyList, tagMap):
        '''Fills rdfGraph with keys and tags.'''
        keyScheme = self.rdfGraph.addConceptScheme(self.keySchemeName, self.keySchemeTitle, self.creator)
        tagScheme = self.rdfGraph.addConceptScheme(self.tagSchemeName, self.tagSchemeTitle, self.creator)

        totalParts = self.numberKeys + self.numberTags
        atPart = 1
        for filteredKey in self.filterUtil.exactKeyFilter:
            self.console.printPercent(partInt=atPart, totalInt=totalParts, workingOn='Key: ' + filteredKey)
            keyConcept = self.createKey(filteredKey, keyScheme)
            atPart = atPart + 1

        for key in keyList:
            self.printPercent(partInt=atPart, totalInt=totalParts, workingOn='Key: ' + key)
            keyConcept = self.createKey(key, keyScheme)
            atPart = atPart + 1

            valueList = tagMap.get(key)
            if valueList is None or len(valueList) == 0:
                continue
            for value in valueList:
                self.printPercent(partInt=atPart, totalInt=totalParts, workingOn='Tag: ' + key + '=' + value)
                self.createTag(key, keyConcept, value, tagScheme)
                atPart = atPart + 1

    def impliesToConcept(self):
        for subject, obj in self.rdfGraph.getSubObjOSMImplies():
            foundConcept = self.rdfGraph.getSubByPrefLabel(str(obj))
            if foundConcept is not None:
                self.rdfGraph.removeOSMImpliesLiteral(str(subject), str(obj))
                self.rdfGraph.addOSMImpliesURIRef(str(subject), foundConcept)

    def combinesToConcept(self):
        for subject, obj in self.rdfGraph.getSubObjOSMCombines():
            foundConcept = self.rdfGraph.getSubByPrefLabel(str(obj))
            if foundConcept is not None:
                self.rdfGraph.removeOSMCombinesLiteral(str(subject), str(obj))
                self.rdfGraph.addOSMCombinesURIRef(str(subject), foundConcept)

    def linksToConcept(self):
        for subject, obj in self.rdfGraph.getSubObjOSMLinks():
            foundConcept = self.rdfGraph.getSubByPrefLabel(str(obj))
            if foundConcept is not None:
                self.rdfGraph.removeOSMLinksLiteral(str(subject), str(obj))
                self.rdfGraph.addOSMLinksURIRef(str(subject), foundConcept)

    def osmLinksToConcept(self):
        '''Traverse the rdfGraph and replaces OSM Wiki links literals (implies, combines, links)
           to concepts of this rdfGraph, should they exists. Should be done once the rdfGraph
           is created completly.'''
        self.impliesToConcept()
        self.combinesToConcept()
        self.linksToConcept()


'''if __name__ == '__main__':
    startTime = timeit.default_timer()
    retry = True
    console = Console(sys.stdout)
    while retry:
        try:
            bt = BaseThesaurus(console)
            retry = False
        except ConnectionError as ce:
            pass
            console.println(ce)
            console.println('Retrying creating TagFinder BaseThesaurus...')

    endTime = timeit.default_timer()
    elapsed = endTime - startTime
    console.println('\nTime elapsed to generate rdfGraph: ' + str(elapsed / 60) + ' mins')
    console.println('Number of keys: ' + str(bt.numberKeys))
    console.println('Number tags: ' + str(bt.numberTags))
    console.println ('Tripples: ' + str(bt.getBaseGraph().triplesCount()))

    #bt.getBaseGraph()'''
