# -*- coding: utf-8 -*-
'''
Created on 27.09.2014

@author: Simon Gwerder
'''

import requests
import timeit
import datetime

# from requests.adapters import TimeoutSauce

from filter import Filter
import utils
from skosgraph import SkosGraph


# class ConnectionTimeout(TimeoutSauce):
#    def __init__(self, *args, **kwargs):
#        connect = kwargs.get('connect', 5)
#        read = kwargs.get('read', connect)
#        super(ConnectionTimeout, self).__init__(connect=connect, read=read)

# requests.adapters.TimeoutSauce = ConnectionTimeout

# key's that got too many different meaningless values (key still will be added as concept)
minCount = 5

def outputFile(outputName, outputEnding, printDate):
    if printDate:
        dateString = datetime.date.today().isoformat()
        dateString = dateString.replace('-', '')
        dateString = dateString.substring(2, dateString.length)
        return utils.dataDir() + outputName + dateString + outputEnding
    else:
        return utils.dataDir() + outputName + outputEnding


if __name__ == '__main__':

    startTime = timeit.default_timer()

    tagInfoSortDesc = '&sortname=count_all&sortorder=desc'
    tagInfoAllKeys = 'http://taginfo.osm.org/api/4/keys/all?filter=in_wiki'
    tagInfoValueOfKey = 'http://taginfo.osm.org/api/4/key/values?key='
    tagInfoWikiPageOfKey = 'http://taginfo.osm.org/api/4/key/wiki_pages?key='
    tagInfoWikiPageOfTag = 'http://taginfo.osm.org/api/4/tag/wiki_pages?key='  # + &value=blabla
    osmWikiBase = 'http://wiki.openstreetmap.org/wiki/'
    osmSchemeName = 'http://wiki.openstreetmap.org/wiki/Tag'

    outputName = 'osm_tag_thesaurus_'
    outputEnding = '.rdf'


    keyResult = requests.get(tagInfoAllKeys + tagInfoSortDesc);
    keyJson = keyResult.json();
    keyData = keyJson['data'];

    filterUtil = Filter()

    keyCount = 0
    keyList = []


    for keyItem in keyData:
        if keyItem['count_all'] < minCount:
            break;  # speedup because of sorted list
        if not filterUtil.hasKey(keyItem['key']) and utils.validCharsCheck(keyItem['key']) and keyItem['values_all'] >= minCount:
            # keyWikiPage = requests.get(tagInfoWikiPageOfKey + keyItem['key'].replace('%',''))
            # if(len(keyWikiPage.json()) > 0):
            keyList.append(keyItem['key'])
            keyCount = keyCount + 1
            print(str(keyCount) + ' - Key: ' + keyItem['key'])

    print 'Number of keys: ' + str(len(keyList))

    tagMap = {}
    for key in keyList:
        valueResult = requests.get(tagInfoValueOfKey + key + tagInfoSortDesc)
        valueJson = valueResult.json()
        valueData = valueJson['data']

        s = ''
        for valueItem in valueData:
            if not filterUtil.hasValue(valueItem['value']) and valueItem['in_wiki'] and utils.validCharsCheck(valueItem['value']) and valueItem['count'] >= minCount:
                k = tagMap.get(key)
                if(k is not None):
                    k.append(valueItem['value'])
                    s = s + ',  ' + valueItem['value']
                else:
                    k = [valueItem['value']]
                    s = valueItem['value']
                tagMap[key] = k

        print(str(len(tagMap)) + ' : ' + key + '\t\t' + s)


    graph = SkosGraph()

    scheme = graph.addConceptScheme(osmSchemeName)

    keyCount = 0;
    tagCount = 0;
    for key in keyList:
        keyCount = keyCount + 1
        keyConcept = graph.addConcept(osmWikiBase + 'Key:' + key)
        graph.addPrefLabel(keyConcept, key, 'de')

        graph.addInScheme(keyConcept, scheme)
        graph.addHasTopConcept(scheme, keyConcept)

        print(str(keyCount) + '/' + str(len(keyList)) + ' : ' + osmWikiBase + 'Key:' + key)
        valueList = tagMap.get(key)
        if valueList is None:
            continue
        for value in valueList:
            taglink = osmWikiBase + 'Tag:' + key + '=' + value  # before: key + '%3D' + value
            # result = requests.get('http://' + taglink)
            tagWikiPage = requests.get(tagInfoWikiPageOfTag + key + '&value=' + value)
            if len(tagWikiPage.json()) > 0:
                print('\t' + taglink)
                tagWikiPageJson = tagWikiPage.json()
                tagConcept = graph.addConcept(taglink)
                graph.addPrefLabel(tagConcept, key + '=' + value, 'en')
                graph.addBroader(tagConcept, keyConcept)
                graph.addNarrower(keyConcept, tagConcept)
                graph.addInScheme(tagConcept, scheme)
                tagCount = tagCount + 1

                for langItems in tagWikiPageJson:
                    if langItems['lang'] == 'de':
                        description = langItems['description']
                        if not description == '':
                            graph.addScopeNote(tagConcept, description, 'de')
                            print '\t\tde: ' + description
                    elif langItems['lang'] == 'en':
                        description = langItems['description']
                        if  description is not None and not description == '':
                            graph.addScopeNote(tagConcept, description, 'en')
                            print '\t\ten: ' + description
                        imageData = langItems['image']
                        depiction = imageData['image_url']
                        if depiction is not None and not depiction == '':
                            graph.addDepiction(tagConcept, depiction)
                            print '\t\t' + depiction
                    else:
                        continue
    for filteredKey in filterUtil.completeFilterList():
        keyWikiPage = requests.get(tagInfoWikiPageOfKey + filteredKey)
        if len(keyWikiPage.json()) > 0:
            keyConcept = graph.addConcept(osmWikiBase + 'Key:' + filteredKey)
            graph.addPrefLabel(keyConcept, filteredKey, 'de')
            graph.addInScheme(keyConcept, scheme)
            graph.addHasTopConcept(scheme, keyConcept)
            keyCount = keyCount + 1

    graph.serialize(outputFile(outputName, outputEnding, printDate=True))

    print('\n\nKeys: ' + str(keyCount))
    print('Tags: ' + str(tagCount))

    stopTime = timeit.default_timer()

print 'Generated in: ' + str((stopTime - startTime) / 60) + ' minutes'
