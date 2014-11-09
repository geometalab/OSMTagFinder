# -*- coding: utf-8 -*-
'''
Created on 27.09.2014

@author: Simon Gwerder
'''

from requests.exceptions import ConnectionError
import timeit

from filter import Filter
from utilities import utils
from utilities.configloader import ConfigLoader
from thesaurus.rdfgraph import RDFGraph
from externalapi.taginfo import TagInfo
from externalapi.tagupdate import TagInfoUpdate
from utilities.translator import Translator

class BaseThesaurus:

    rdfGraph = RDFGraph()
    tagInfo = TagInfo()
    numberKeys = 0
    numberTags = 0

    cl = ConfigLoader()

    osmWikiBase = cl.getThesaurusString('OSM_WIKI_PAGE')
    keySchemeName = cl.getThesaurusString('KEY_SCHEME_NAME')
    tagSchemeName = cl.getThesaurusString('TAG_SCHEME_NAME')

    outputName = cl.getThesaurusString('OUTPUT_NAME')  # osm_tag_thesaurus
    outputEnding = cl.getThesaurusString('DEFAULT_FORMAT')  # .rdf

    translationHintDE = cl.getThesaurusString('TRANSLATION_HINT_DE')
    translationHintEN = cl.getThesaurusString('TRANSLATION_HINT_EN')

    valueMinCount = cl.getThesaurusInt('MINIMUM_COUNT')

    filterUtil = Filter()
    translator = Translator()

    def __init__(self):
        keyList = self.getListOfValidKeys()

        self.numberKeys = len(keyList) + len(self.filterUtil.exactKeyFilter)

        tagMap = self.bundleToTagMap(keyList)

        self.numberTags = self.numberTags(tagMap)

        empty = []
        for filteredKey in self.filterUtil.exactKeyFilter:
            tagMap[filteredKey] = empty

        self.createGraph(keyList, tagMap)

        self.osmLinksToConcept()

        self.rdfGraph.serialize(utils.outputFile(self.outputName, self.outputEnding, useDateEnding=True))

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
        for keyItem in keyData:
            if keyItem['count_all'] < self.valueMinCount:
                break;  # speedup because of sorted list
            if not self.filterUtil.hasKey(keyItem['key']) and utils.validCharsCheck(keyItem['key']) and keyItem['values_all'] >= self.valueMinCount:
                keyList.append(keyItem['key'])
                print('Key: ' + keyItem['key'])
        return keyList

    def filterTagData(self, key, tagMap, tagData):
        '''Takes the raw key data from 'tagData' and makes validation checks on each
           element. Then the updated 'tagMap' (k:key, v:value) is returned.'''
        r = ''
        for valueItem in tagData:
            if not self.filterUtil.hasValue(valueItem['value']) and valueItem['in_wiki'] and utils.validCharsCheck(valueItem['value']) and valueItem['count'] >= self.valueMinCount:
                k = tagMap.get(key)
                if k is not None:
                    k.append(valueItem['value'])
                    r = r + ',  ' + valueItem['value']
                else:
                    k = [valueItem['value']]
                    r = valueItem['value']
                tagMap[key] = k
        print(key + '\t\t' + r)
        return tagMap

    def bundleToTagMap(self, keyList):
        '''Creates a hash map with k:key and v:value of valid keys and values.'''
        tagMap = {}
        for key in keyList:
            tagData = self.tagInfo.getAllTagData(key)
            tagMap = self.filterTagData(key, tagMap, tagData)
        return tagMap

    def addImageScopeNote(self, concept, wikiPageJson):
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
                    scopeNoteDE = temp
                    print '\t\tde: ' + scopeNoteDE
            elif wikiData['lang'] == 'en':
                temp = wikiData['description']
                if  temp is not None and not temp == '':
                    temp = temp.replace('\'', '')
                    scopeNoteEN = temp
                    print '\t\ten: ' + scopeNoteEN
                    imageData = wikiData['image']
                    depiction = imageData['image_url']
            if depiction is None or depiction == '':
                imageData = wikiData['image']
                depiction = imageData['image_url']

        if scopeNoteDE == '' and not scopeNoteEN == '':
            self.rdfGraph.addScopeNote(concept, scopeNoteEN, 'en')
            self.rdfGraph.addScopeNote(concept, self.translator.translateENtoDE(scopeNoteEN) + ' ' + self.translationHintDE, 'de')
        elif not scopeNoteDE == '' and scopeNoteEN == '':
            self.rdfGraph.addScopeNote(concept, self.translator.translateDEtoEN(scopeNoteDE) + ' ' + self.translationHintEN, 'en')
            self.rdfGraph.addScopeNote(concept, scopeNoteDE, 'de')
        elif not scopeNoteDE == '' and not scopeNoteEN == '':
            self.rdfGraph.addScopeNote(concept, scopeNoteEN, 'en')
            self.rdfGraph.addScopeNote(concept, scopeNoteDE, 'de')

        if depiction is not None and not depiction == '':
            self.rdfGraph.addDepiction(concept, depiction)
            print '\t\t' + depiction

    def updateTagStats(self, concept, key, value=None, wikiPageJson=None):
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
            if not onNode and not onWay and not onRelation:
                onArea = True
            else:
                onArea = tagInfoUpdate.getOnArea()

            nodeStr = '{ "count": "' + str(tagInfoUpdate.getCountNodes()) + '", "use": "' + str(onNode) + '" }'
            wayStr = '{ "count": "' + str(tagInfoUpdate.getCountWays()) + '", "use": "' + str(onWay) + '" }'
            areaStr = '{ "count": "0"' + ', "use": "' + str(onArea) + '" }'
            relationStr = '{ "count": "' + str(tagInfoUpdate.getCountRelations()) + '", "use": "' + str(onRelation) + '" }'

        self.rdfGraph.addOSMNode(concept, nodeStr)
        self.rdfGraph.addOSMWay(concept, wayStr)
        self.rdfGraph.addOSMArea(concept, areaStr)
        self.rdfGraph.addOSMRelation(concept, relationStr)

    def updateTagLinks(self, concept, key, value=None, wikiPageJson=None):
        '''Updates the tag links from OSM wiki: implies, combinations and linked. Just as Literals.'''
        tagInfoUpdate = TagInfoUpdate(key=key, value=value, wikiPageJson=wikiPageJson)

        listImplies = tagInfoUpdate.getListImplies()
        listCombinations = tagInfoUpdate.getListCombinations()
        listLinked = tagInfoUpdate.getListLinked()

        impliesStr = '\t\tImplies: '
        for tagImplies in listImplies: #tags or keys
            self.rdfGraph.addOSMImpliesLiteral(concept, tagImplies)
            impliesStr = impliesStr + tagImplies + ', '
        print(impliesStr[:-2])

        combinesStr = '\t\tCombines: '
        for tagCombines in listCombinations: #tags or keys
            self.rdfGraph.addOSMCombinesLiteral(concept, tagCombines)
            combinesStr = combinesStr + tagCombines + ', '
        print(combinesStr[:-2])

        linksStr = '\t\tLinks: '
        for tagLinks in listLinked: #tags or keys
            self.rdfGraph.addOSMLinksLiteral(concept, tagLinks)
            linksStr = linksStr + tagLinks + ', '
        print(linksStr[:-2])

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
            self.addImageScopeNote(keyConcept, keyWikiPageJson)


        return keyConcept

    def createTag(self, key, keyConcept, value, tagScheme):
        '''Adds value with name 'key'='value' to the rdfGraph, with as much wiki information as possible.'''
        taglink = self.osmWikiBase + 'Tag:' + key + '=' + value  # before: key + '%3D' + value
        # result = requests.get('http://' + taglink)
        tagWikiPageJson = self.tagInfo.getWikiPageOfTag(key, value)
        if len(tagWikiPageJson) > 0:
            print('\t' + taglink)
            tagConcept = self.rdfGraph.addConcept(taglink)
            self.rdfGraph.addInScheme(tagConcept, tagScheme)
            self.rdfGraph.addPrefLabel(tagConcept, key + '=' + value)
            self.rdfGraph.addBroader(tagConcept, keyConcept)
            self.rdfGraph.addNarrower(keyConcept, tagConcept)

            self.updateTagStats(concept=tagConcept, key=key, value=value, wikiPageJson=tagWikiPageJson)
            self.updateTagLinks(concept=tagConcept, key=key, value=value, wikiPageJson=tagWikiPageJson)

            self.addImageScopeNote(tagConcept, tagWikiPageJson)

    def createGraph(self, keyList, tagMap):
        '''Fills rdfGraph with keys and tags.'''
        keyScheme = self.rdfGraph.addConceptScheme(self.keySchemeName)
        tagScheme = self.rdfGraph.addConceptScheme(self.tagSchemeName)

        for key in keyList:
            keyConcept = self.createKey(key, keyScheme)

            print(self.osmWikiBase + 'Key:' + key)
            valueList = tagMap.get(key)
            if valueList is None:
                continue
            for value in valueList:
                self.createTag(key, keyConcept, value, tagScheme)

    def impliesToConcept(self):
        for subject, obj in self.rdfGraph.getSubObjOSMImplies():
            foundConcept = self.rdfGraph.getSubByPrefLabel(str(obj))
            if foundConcept is not None:
                self.rdfGraph.removeOSMImpliesLiteral(str(subject), str(obj))
                self.rdfGraph.addOSMImpliesURIRef(str(subject), foundConcept)
                print('Replacing implies: ' + str(obj) + '\tto: ' + str(foundConcept))

    def combinesToConcept(self):
        for subject, obj in self.rdfGraph.getSubObjOSMCombines():
            foundConcept = self.rdfGraph.getSubByPrefLabel(str(obj))
            if foundConcept is not None:
                self.rdfGraph.removeOSMCombinesLiteral(str(subject), str(obj))
                self.rdfGraph.addOSMCombinesURIRef(str(subject), foundConcept)
                print('Replacing combines: ' + str(obj) + '\tto: ' + str(foundConcept))

    def linksToConcept(self):
        for subject, obj in self.rdfGraph.getSubObjOSMLinks():
            foundConcept = self.rdfGraph.getSubByPrefLabel(str(obj))
            if foundConcept is not None:
                self.rdfGraph.removeOSMLinksLiteral(str(subject), str(obj))
                self.rdfGraph.addOSMLinksURIRef(str(subject), foundConcept)
                print('Replacing links: ' + str(obj) + '\tto: ' + str(foundConcept))

    def osmLinksToConcept(self):
        '''Traverse the rdfGraph and replaces OSM Wiki links literals (implies, combines, links)
           to concepts of this rdfGraph, should they exists. Should be done once the rdfGraph
           is created completly.'''
        self.impliesToConcept()
        self.combinesToConcept()
        self.linksToConcept()






if __name__ == '__main__':
    startTime = timeit.default_timer()
    retry = True
    while retry:
        try:
            bt = BaseThesaurus()
            retry = False
        except ConnectionError as ce:
            print(ce)
            print('Retrying creating BaseGraph')

    endTime = timeit.default_timer()
    elapsed = endTime - startTime
    print('\nTime elapsed to generate rdfGraph: ' + str(elapsed / 60) + ' mins')
    print('Number of keys: ' + str(bt.numberKeys))
    print('Number tags: ' + str(bt.numberTags))
    print ('Tripples: ' + str(bt.getBaseGraph().triplesCount()))

    bt.getBaseGraph()
