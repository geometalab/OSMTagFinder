# -*- coding: utf-8 -*-
'''
Created on 01.12.2014

@author: Simon Gwerder
'''

import json
from ordered_set import OrderedSet
import requests

from utilities import utils
from utilities.retry import retry
import timeit

class IDPreset:
    name = None
    terms = []
    tags = []

    def __init__(self):
        self.name = None
        self.terms = []
        self.tags = []

class IDPresetsSetup:

    idPresets = OrderedSet()

    def getIDPresets(self):
        return self.idPresets

    def __init__(self, presetFilePath):
        if presetFilePath is None: return
        fileHandler = open(presetFilePath)

        jsonData = json.load(fileHandler)

        iterList = []
        for item in jsonData:
            iterList.append(item)

        iterList.sort()

        for item in iterList:
            if item.count('/') > 1: continue
            idPreset = IDPreset()
            if 'name' in jsonData[item]:
                idPreset.name = jsonData[item]['name']
            else:
                continue
            if 'tags' in jsonData[item]:
                for key in jsonData[item]['tags']:
                    if key is not 'name':
                        tag = key + '=' + jsonData[item]['tags'][key]
                        idPreset.tags.append(tag)
            else:
                continue
            idPreset.terms.append(idPreset.name)
            if 'terms' in jsonData[item]:
                for term in jsonData[item]['terms']:
                    idPreset.terms.append(term)
            self.idPresets.append(idPreset)

        fileHandler.close()

class TestRun:

    tagFinderAPI = 'http://localhost:5000/api/search?q='

    @retry(Exception, tries=3)
    def apiCallTagfinder(self, searchTerm):
        response = requests.get(self.tagFinderAPI + searchTerm)
        #response = urllib.urlopen(self.tagFinderAPI + searchTerm)
        if response.status_code < 300:
            return response.json()
        return None

    def getTagDictFromCall(self, responseJson):
        retDict = { }
        for tfTag in responseJson:
            prefLabel = tfTag['prefLabel']
            if not '=' in prefLabel: # is a key
                prefLabel = prefLabel + '=*'
            retDict[prefLabel] = tfTag['searchMeta']
        return retDict

    def __init__(self, idPresetsSetup):

        print 'IDEDITOR PRESET TESTS'
        current = 1
        testTotal = len(idPresetsSetup.getIDPresets())
        nameTotal = len(idPresetsSetup.getIDPresets())
        altTermTotal = -nameTotal # they are also contained in the terms list, for convenient search
        testFound = 0
        nameFound = 0
        altTermFound = 0
        for idPreset in idPresetsSetup.getIDPresets():
            titleStr = '\n\nTest ' + str(current) + '/' + str(len(idPresetsSetup.getIDPresets())) + ' - Name: ' + idPreset.name
            print titleStr
            print '=' * 60
            print 'Tags: ' + ", ".join(idPreset.tags)
            found = False
            for term in idPreset.terms:
                responseJson = self.apiCallTagfinder(term)
                if responseJson is None:
                    print 'Call failed!'
                else:
                    foundList = self.getTagDictFromCall(responseJson)
                    interSectionSet = set(idPreset.tags).intersection(set(foundList.keys()))
                    if len(interSectionSet) == 0:
                        print '{0}{1:<20s}{2}'.format('Term: ', term, ' > none found')
                    else:
                        found = True
                        print '{0}{1:<20s}{2}{3}'.format('Term: ', term, ' > found: ', ', '.join(interSectionSet))
                        #for searchMeta in foundList.values():
                        #    print searchMeta
                        if term is idPreset.name:
                            nameFound = nameFound + 1
                        else:
                            altTermFound = altTermFound + 1
                altTermTotal = altTermTotal + 1

            if found:
                testFound = testFound + 1
            current = current + 1

        print '\n\n'
        print '=' * 60
        print '=' * 60
        print 'Found test tags  : ' + str(testFound) + '/' + str(testTotal)
        print 'Found \"names\"    : ' + str(nameFound) + '/' + str(nameTotal)
        print 'Found \"terms\"  : ' + str(altTermFound) + '/' + str(altTermTotal)




if __name__ == '__main__':

    startTime = timeit.default_timer()

    setup = IDPresetsSetup(utils.testDir() + 'blackboxtests.json')

    #TagFinder needs to be running. Can also start TagFinder locally here.
    TestRun(setup)

    endTime = timeit.default_timer()
    elapsed = endTime - startTime
    print '\nTime elapsed running test: ' + str(elapsed / 60) + ' mins'








