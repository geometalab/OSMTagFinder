# -*- coding: utf-8 -*-
'''
Created on 27.09.2014

@author: Simon Gwerder
'''

# from requests.adapters import TimeoutSauce
import requests
from requests.exceptions import ConnectionError
import timeit
import datetime

from filter import Filter
from utilities import utils
from utilities.configloader import ConfigLoader
from thesaurus.rdfgraph import RDFGraph
from utilities.translator import Translator

class BaseThesaurus:

    graph = RDFGraph()
    numberKeys = 0
    numberTags = 0

    cl = ConfigLoader()
    tagInfoSortDesc = cl.getTagInfoAPIString('SORT_DESC')
    tagInfoAllKeys = cl.getTagInfoAPIString('ALL_KEYS')
    tagInfoValueOfKey = cl.getTagInfoAPIString('VALUE_OF_KEY')
    tagInfoWikiPageOfKey = cl.getTagInfoAPIString('WIKI_PAGE_OF_KEY')
    tagInfoWikiPageOfTag = cl.getTagInfoAPIString('WIKI_PAGE_OF_TAG')
    tagInfoTagPostfix = cl.getTagInfoAPIString('TAG_POSTFIX')

    osmWikiBase = cl.getThesaurusString('OSM_WIKI_PAGE')
    keySchemeName = cl.getThesaurusString('KEY_SCHEME_NAME')
    tagSchemeName = cl.getThesaurusString('TAG_SCHEME_NAME')

    outputName = cl.getThesaurusString('OUTPUT_NAME')  # osm_tag_thesaurus
    outputEnding = cl.getThesaurusString('DEFAULT_FORMAT')  # .rdf

    translationHintDE = cl.getThesaurusString('TRANSLATION_HINT_DE')
    translationHintEN = cl.getThesaurusString('TRANSLATION_HINT_EN')

    minCount = cl.getThesaurusInt('MINIMUM_COUNT')

    filterUtil = Filter()

    def __init__(self):
        keyData = self.tagInfoGetKeyData()
        keyList = self.filterKeyData(keyData)

        self.numberKeys = len(keyList) + len(self.filterUtil.exactKeyFilter)

        tagMap = self.getTagMap(keyList)

        self.numberTags = self.numberTags(tagMap)

        empty = []
        for filteredKey in self.filterUtil.exactKeyFilter:
            tagMap[filteredKey] = empty

        self.createGraph(keyList, tagMap)

        self.graph.serialize(self.outputFile(self.outputName, self.outputEnding, hasDateEnding=True))

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

    def tagInfoGetKeyData(self):
        '''Calls TagInfo for a list of all keys. The list is descending sorted by count of
           values attached to the key.'''
        keyResult = requests.get(self.tagInfoAllKeys + self.tagInfoSortDesc);
        keyJson = keyResult.json();
        return keyJson['data'];

    def filterKeyData(self, keyData):
        '''Takes the raw key data from 'keyData' and makes validation checks on each
           element. Then a list of valid keys is returned.'''
        keyList = []
        for keyItem in keyData:
            if keyItem['count_all'] < self.minCount:
                break;  # speedup because of sorted list
            if not self.filterUtil.hasKey(keyItem['key']) and utils.validCharsCheck(keyItem['key']) and keyItem['values_all'] >= self.minCount:
                # keyWikiPage = requests.get(tagInfoWikiPageOfKey + keyItem['key'].replace('%',''))
                # if(len(keyWikiPage.json()) > 0):
                keyList.append(keyItem['key'])
                print('Key: ' + keyItem['key'])
        return keyList

    def tagInfoGetTagData(self, key):
        '''Calls TagInfo for a list of all tags for 'key'. The list is descending sorted by count of
        occurrence in OSM.'''
        tagResult = requests.get(self.tagInfoValueOfKey + key + self.tagInfoSortDesc)
        tagJson = tagResult.json()
        return tagJson['data']

    def filterTagData(self, key, tagMap, tagData):
        '''Takes the raw key data from 'tagData' and makes validation checks on each
           element. Then the updated 'tagMap' (k:key, v:tag) is returned.'''
        r = ''
        for valueItem in tagData:
            if not self.filterUtil.hasValue(valueItem['value']) and valueItem['in_wiki'] and utils.validCharsCheck(valueItem['value']) and valueItem['count'] >= self.minCount:
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

    def getTagMap(self, keyList):
        '''Creates a hash map with k:key and v:tag of valid keys and tags.'''
        tagMap = {}
        for key in keyList:
            tagData = self.tagInfoGetTagData(key)
            tagMap = self.filterTagData(key, tagMap, tagData)
        return tagMap

    def createKey(self, key, keyScheme):
        '''Adds key with name 'key' to the graph, with as much wiki information as possible.'''
        keyConcept = self.graph.addConcept(self.osmWikiBase + 'Key:' + key)
        self.graph.addPrefLabel(keyConcept, key)
        self.graph.addInScheme(keyConcept, keyScheme)
        # graph.addHasTopConcept(keyScheme, keyConcept)

        keyWikiPage = requests.get(self.tagInfoWikiPageOfKey + key)
        keyWikiPageJson = keyWikiPage.json()
        if len(keyWikiPageJson) > 0:
            depiction = ''
            for wikiData in keyWikiPageJson:
                if wikiData['lang'] == 'de':
                    if depiction == '':
                        imageData = wikiData['image']
                        depiction = imageData['image_url']
                elif wikiData['lang'] == 'en':
                    imageData = wikiData['image']
                    depiction = imageData['image_url']
            if depiction is not None and not depiction == '':
                self.graph.addDepiction(keyConcept, depiction)
                print '\t\t' + depiction

        return keyConcept

    def createTag(self, key, keyConcept, tag, tagScheme):
        '''Adds tag with name 'tag' to the graph, with as much wiki information as possible.'''
        translator = Translator()

        taglink = self.osmWikiBase + 'Tag:' + key + '=' + tag  # before: key + '%3D' + tag
        # result = requests.get('http://' + taglink)
        tagWikiPage = requests.get(self.tagInfoWikiPageOfTag + key + self.tagInfoTagPostfix + tag)
        tagWikiPageJson = tagWikiPage.json()
        if len(tagWikiPageJson) > 0:
            print('\t' + taglink)
            tagConcept = self.graph.addConcept(taglink)
            self.graph.addPrefLabel(tagConcept, key + '=' + tag)
            self.graph.addBroader(tagConcept, keyConcept)
            self.graph.addNarrower(keyConcept, tagConcept)
            self.graph.addInScheme(tagConcept, tagScheme)

            descriptionDE = ''
            descriptionEN = ''
            depiction = ''

            for wikiData in tagWikiPageJson:

                if wikiData['lang'] == 'de':
                    temp = wikiData['description']
                    if temp is not None and not temp == '':
                        descriptionDE = temp
                        print '\t\tde: ' + descriptionDE
                    if depiction == '':
                        imageData = wikiData['image']
                        depiction = imageData['image_url']
                elif wikiData['lang'] == 'en':
                    temp = wikiData['description']
                    if  temp is not None and not temp == '':
                        descriptionEN = temp
                        print '\t\ten: ' + descriptionEN
                        imageData = wikiData['image']
                        depiction = imageData['image_url']

            if descriptionDE == '' and not descriptionEN == '':
                self.graph.addScopeNote(tagConcept, descriptionEN, 'en')
                self.graph.addScopeNote(tagConcept, translator.translateENtoDE(descriptionEN) + ' ' + self.translationHintDE, 'de')
            elif not descriptionDE == '' and descriptionEN == '':
                self.graph.addScopeNote(tagConcept, translator.translateDEtoEN(descriptionDE) + ' ' + self.translationHintEN, 'en')
                self.graph.addScopeNote(tagConcept, descriptionDE, 'de')
            elif not descriptionDE == '' and not descriptionEN == '':
                self.graph.addScopeNote(tagConcept, descriptionEN, 'en')
                self.graph.addScopeNote(tagConcept, descriptionDE, 'de')

            if depiction is not None and not depiction == '':
                self.graph.addDepiction(tagConcept, depiction)
                print '\t\t' + depiction

    def createGraph(self, keyList, tagMap):
        '''Fills graph with keys and tags.'''
        keyScheme = self.graph.addConceptScheme(self.keySchemeName)
        tagScheme = self.graph.addConceptScheme(self.tagSchemeName)

        for key in keyList:
            keyConcept = self.createKey(key, keyScheme)

            print(self.osmWikiBase + 'Key:' + key)
            tagList = tagMap.get(key)
            if tagList is None:
                continue
            for tag in tagList:
                self.createTag(key, keyConcept, tag, tagScheme)

    def outputFile(self, outputName, outputEnding, hasDateEnding):
        '''Returns full file path. If 'hasDateEnding' is True, a date postfix is added between
           the filename and ending, of the form '_yymmdd'.'''
        if hasDateEnding:
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
        except ConnectionError  as ce:
            print(ce)
            print('Retrying creating BaseGraph')

    endTime = timeit.default_timer()
    elapsed = endTime - startTime
    print('\nTime elapsed to generate graph: ' + str(elapsed / 60) + ' mins')
    print('Number of keys: ' + str(bt.numberKeys))
    print('Number tags: ' + str(bt.numberTags))
    print ('Tripples: ' + str(bt.graph.tripplesCount()))

    bt.getBaseGraph()
