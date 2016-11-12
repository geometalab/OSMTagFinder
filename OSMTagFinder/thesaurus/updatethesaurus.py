# -*- coding: utf-8 -*-
'''
Created on 04.12.2014

@author: Simon Gwerder
'''

from thesaurus.basethesaurus import BaseThesaurus
from thesaurus.filter import Filter
from thesaurus.indexer import Indexer
from thesaurus.mapsemnet import MapOSMSemanticNet
from utilities import utils
from utilities.configloader import ConfigLoader
from utilities.translator import Translator


class UpdateThesaurus:

    rdfGraph = None
    cl = ConfigLoader()
    bt = None
    tagInfo = None

    osmWikiBase = cl.getThesaurusString('OSM_WIKI_PAGE')
    keySchemeName = cl.getThesaurusString('KEY_SCHEME_NAME')
    tagSchemeName = cl.getThesaurusString('TAG_SCHEME_NAME')

    translationHintDE = cl.getThesaurusString('TRANSLATION_HINT_DE')
    translationHintEN = cl.getThesaurusString('TRANSLATION_HINT_EN')
    editNote = cl.getThesaurusString('NO_TERM')

    valueMinCount = cl.getThesaurusInt('MINIMUM_COUNT')

    translator = Translator()
    filterUtil = Filter()

    def __init__(self, tagInfo, rdfGraph, console=None):
        if rdfGraph is None: return
        if tagInfo is None: return

        self.rdfGraph = rdfGraph
        self.tagInfo = tagInfo
        self.bt = BaseThesaurus(tagInfo=self.tagInfo, rdfGraph=self.rdfGraph, console=console)
        self.bt.printMessage('Updating rdfGraph! Currently ' + str(rdfGraph.triplesCount()) + ' triples')
        self.bt.printMessage('\nGetting all valid keys:')
        keyList = self.bt.getListOfValidKeys()
        self.bt.printMessage('\nGetting all valid tags:')
        tagMap = self.bt.bundleToTagMap(keyList)
        for filteredKey in self.filterUtil.exactKeyFilter:
            keyList.append(filteredKey)

        self.handleKeys(keyList)
        self.handleTags(self.getTagList(tagMap))

        self.bt.printMessage('\nManage links and concepts')
        self.bt.osmLinksToConcept()

        self.bt.printMessage('\nCreate mapping to OSM Semantic Net')
        osnSemNetFilePath = utils.semnetDir() + 'osm_semantic_network.rdf'
        MapOSMSemanticNet(self.rdfGraph, osnSemNetFilePath)

        self.bt.printMessage('\nFinished. Serializing rdfGraph: New ' + str(rdfGraph.triplesCount()) + ' triples')
        self.rdfGraph.serialize(rdfGraph.filePath)

        self.bt.printMessage('\nStarting Indexer')
        Indexer(self.rdfGraph) # will index it anew
        self.bt.printMessage('\nFinished updating')
        print 'done'

    def handleNewKeys(self, keyList):
        current = 1
        for key in keyList:
            keyConcept = self.bt.createKey(key, self.keySchemeName)
            if keyConcept:
                self.bt.printMessage(str(current) + '/' + str(len(keyList)) + ' - Created new key with subject: ' + keyConcept)
            else:
                self.bt.printMessage(str(current) + '/' + str(len(keyList)) + ' - Could not create: ' + key + ' no wikipage found')
            current = current + 1

    def handleNewTags(self, tagList):
        current = 1
        for tag in tagList:
            key = tag.split('=')[0]
            value = tag.split('=')[1]
            keyConcept = self.osmWikiBase + 'Key:' + key # this key either exists already or was created just before.
            test = utils.genGetFirstItem(self.rdfGraph.getPrefLabel(keyConcept))
            if not test: # making sure it really exists
                keyConcept = self.bt.createKey(key, self.keySchemeName)
                if keyConcept:
                    self.bt.printMessage(str(current) + '/' + str(len(tagList)) + ' - Created new key with subject: ' + keyConcept)
            tagConcept = self.bt.createTag(key, keyConcept, value, self.tagSchemeName)
            if tagConcept:
                self.bt.printMessage(str(current) + '/' + str(len(tagList)) + ' - Created new tag with subject: ' + tagConcept)
            else:
                self.bt.printMessage(str(current) + '/' + str(len(tagList)) + ' - Could not create: ' + key + '=' + value + ' no wikipage found')
            current = current + 1

    def removeStats(self, subject):
        default = '{ "count": "0", "use": "False" }'
        self.rdfGraph.setOSMNode(subject, default)
        self.rdfGraph.setOSMWay(subject, default)
        self.rdfGraph.setOSMArea(subject, default)
        self.rdfGraph.setOSMRelation(subject, default)

    def handleDepricated(self, depricatedSubjects):
        current = 1
        for subject in depricatedSubjects:
            self.removeStats(subject)
            self.bt.printMessage(str(current) + '/' + str(len(depricatedSubjects)) + ' - Resetted stats for depricated subject: ' + subject)
            current = current + 1

    def handleUpdateKeys(self, keysToUpdate):
        current = 1
        for keyConcept in keysToUpdate:
            key = keyConcept.split('Key:')[1]
            keyWikiPageJson = self.tagInfo.getWikiPageOfKey(key)
            if len(keyWikiPageJson) > 0:
                self.bt.updateTagStats(concept=keyConcept, key=key, wikiPageJson=keyWikiPageJson, new=False)
                self.bt.addDepictionScopeNote(concept=keyConcept, wikiPageJson=keyWikiPageJson, new=False)
                self.bt.updateTagLinks(concept=keyConcept, key=key, value=None, wikiPageJson=keyWikiPageJson, new=False)
                self.bt.printMessage(str(current) + '/' + str(len(keysToUpdate)) + ' - Updated stats, depiction, links and scopeNote for key subject: ' + keyConcept)
            current = current + 1

    def handleUpdateTags(self, tagsToUpdate):
        current = 1
        for tagConcept in tagsToUpdate:
            tag = tagConcept.split('Tag:')[1]
            key = tag.split('=')[0]
            value = tag.split('=')[1]
            tagWikiPageJson = self.tagInfo.getWikiPageOfTag(key, value)
            if len(tagWikiPageJson) > 0:
                self.bt.updateTagStats(concept=tagConcept, key=key, value=value, wikiPageJson=tagWikiPageJson, new=False)
                self.bt.addDepictionScopeNote(concept=tagConcept, wikiPageJson=tagWikiPageJson, new=False)
                self.bt.updateTagLinks(concept=tagConcept, key=key, value=None, wikiPageJson=tagWikiPageJson, new=False)
                self.bt.printMessage(str(current) + '/' + str(len(tagsToUpdate)) + ' - Updated stats, depiction, links and scopeNote for tag subject: ' + tagConcept)
            current = current + 1

    def handleKeys(self, keyList):
        keysToUpdate = []
        depricatedKeys = []

        # split the keys up into those that need updatecheck, are depricated or new. The new ones will be in 'keyList'
        rdfKeysSubjects = utils.genToList(self.rdfGraph.getSubByScheme(self.keySchemeName))
        for keySubject in rdfKeysSubjects:
            key = keySubject.split('Key:')[1]
            if key in keyList:
                keysToUpdate.append(self.osmWikiBase + 'Key:' + key)
                keyList.remove(key)
            else:
                depricatedKeys.append(self.osmWikiBase + 'Key:' + key)

        self.bt.printMessage('\nCreating new keys:')
        self.handleNewKeys(keyList)
        self.bt.printMessage('\nResetting depricated keys:')
        self.handleDepricated(depricatedKeys)
        self.bt.printMessage('\nUpdate existing keys:')
        self.handleUpdateKeys(keysToUpdate)

    def handleTags(self, tagList):
        tagsToUpdate = []
        depricatedTags = []

        # split the tags up into those that need updatecheck, are depricated or new. The new ones will be in 'tagList'
        rdfTagsSubjects = utils.genToList(self.rdfGraph.getSubByScheme(self.tagSchemeName))
        for tagSubject in rdfTagsSubjects:
            tag = tagSubject.split('Tag:')[1]
            if tag in tagList:
                tagsToUpdate.append(self.osmWikiBase + 'Tag:' + tag)
                tagList.remove(tag)
            else:
                depricatedTags.append(self.osmWikiBase + 'Tag:' + tag)

        self.bt.printMessage('\nCreating new tags:')
        self.handleNewTags(tagList)
        self.bt.printMessage('\nResetting depricated tags:')
        self.handleDepricated(depricatedTags)
        self.bt.printMessage('\nUpdate existing tags:')
        self.handleUpdateTags(tagsToUpdate)

    def getTagList(self, tagMap):
        tagList = []
        for key in tagMap:
            connectedValues = tagMap[key]
            if connectedValues is None or len(connectedValues) == 0:
                continue
            for value in connectedValues:
                tagList.append(key + '=' + value)
        return tagList




