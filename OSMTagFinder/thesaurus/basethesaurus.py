# -*- coding: utf-8 -*-
'''
Created on 27.09.2014

@author: Simon Gwerder
'''

from requests.exceptions import ConnectionError
import timeit
import datetime

from filter import Filter
from utilities import utils
from utilities.configloader import ConfigLoader
from thesaurus.rdfgraph import RDFGraph
from externalapi.taginfo import TagInfo
from externalapi.tagstats import TagStats
from utilities.translator import Translator

from externalapi.thesauri import Thesauri

class BaseThesaurus:

    graph = RDFGraph()
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

        self.graph.serialize(self.outputFile(self.outputName, self.outputEnding, useDateEnding=True))

    def numberTags(self, tagMap):
        '''Returns number of tags in 'tagMap'.'''
        count = 0
        for key in tagMap:
            listValues = tagMap[key]
            count = count + len(listValues)
        return count

    def getBaseGraph(self):
        '''Getter for the base graph.'''
        return self.graph

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
            self.graph.addScopeNote(concept, scopeNoteEN, 'en')
            self.graph.addScopeNote(concept, self.translator.translateENtoDE(scopeNoteEN) + ' ' + self.translationHintDE, 'de')
        elif not scopeNoteDE == '' and scopeNoteEN == '':
            self.graph.addScopeNote(concept, self.translator.translateDEtoEN(scopeNoteDE) + ' ' + self.translationHintEN, 'en')
            self.graph.addScopeNote(concept, scopeNoteDE, 'de')
        elif not scopeNoteDE == '' and not scopeNoteEN == '':
            self.graph.addScopeNote(concept, scopeNoteEN, 'en')
            self.graph.addScopeNote(concept, scopeNoteDE, 'de')

        if depiction is not None and not depiction == '':
            self.graph.addDepiction(concept, depiction)
            print '\t\t' + depiction

    def addStats(self, concept, key, value=None):
        tagStats = TagStats(key, value)
        self.graph.addOSMNode(concept, tagStats.getCountNodes())
        self.graph.addOSMWay(concept, tagStats.getCountWays())
        self.graph.addOSMRelation(concept, tagStats.getCountRelations())

    def createKey(self, key, keyScheme):
        '''Adds key with name 'key' to the graph, with as much wiki information as possible.'''
        keyConcept = self.graph.addConcept(self.osmWikiBase + 'Key:' + key)
        self.graph.addInScheme(keyConcept, keyScheme)
        self.graph.addPrefLabel(keyConcept, key)

        self.addStats(keyConcept, key)
        # graph.addHasTopConcept(keyScheme, keyConcept)

        keyWikiPageJson = self.tagInfo.getWikiPageOfKey(key)
        if len(keyWikiPageJson) > 0:
            self.addImageScopeNote(keyConcept, keyWikiPageJson)


        return keyConcept

    def createTag(self, key, keyConcept, value, tagScheme):
        '''Adds value with name 'key'='value' to the graph, with as much wiki information as possible.'''
        taglink = self.osmWikiBase + 'Tag:' + key + '=' + value  # before: key + '%3D' + value
        # result = requests.get('http://' + taglink)
        tagWikiPageJson = self.tagInfo.getWikiPageOfTag(key, value)
        if len(tagWikiPageJson) > 0:
            print('\t' + taglink)
            tagConcept = self.graph.addConcept(taglink)
            self.graph.addInScheme(tagConcept, tagScheme)
            self.graph.addPrefLabel(tagConcept, key + '=' + value)
            self.graph.addBroader(tagConcept, keyConcept)
            self.graph.addNarrower(keyConcept, tagConcept)

            self.addStats(tagConcept, key, value)

            self.addImageScopeNote(tagConcept, tagWikiPageJson)

    def createGraph(self, keyList, tagMap):
        '''Fills graph with keys and tags.'''
        keyScheme = self.graph.addConceptScheme(self.keySchemeName)
        tagScheme = self.graph.addConceptScheme(self.tagSchemeName)

        for key in keyList:
            keyConcept = self.createKey(key, keyScheme)

            print(self.osmWikiBase + 'Key:' + key)
            valueList = tagMap.get(key)
            if valueList is None:
                continue
            for value in valueList:
                self.createTag(key, keyConcept, value, tagScheme)

    def outputFile(self, outputName, outputEnding, useDateEnding):
        '''Returns full file path. If 'useDateEnding' is True, a date postfix is added between
           the filename and ending, of the form '_yymmdd'.'''
        if useDateEnding:
            dateString = datetime.date.today().isoformat()
            dateString = dateString.replace('-', '')
            dateString = dateString[2:]  # substring from incl. 3rd char to end of string
            return utils.dataDir() + outputName + '_' + dateString + outputEnding
        else:
            return utils.dataDir() + outputName + outputEnding

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
    print('\nTime elapsed to generate graph: ' + str(elapsed / 60) + ' mins')
    print('Number of keys: ' + str(bt.numberKeys))
    print('Number tags: ' + str(bt.numberTags))
    print ('Tripples: ' + str(bt.getBaseGraph().tripplesCount()))

    bt.getBaseGraph()
