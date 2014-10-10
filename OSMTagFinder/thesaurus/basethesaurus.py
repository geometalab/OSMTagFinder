# -*- coding: utf-8 -*-
'''
Created on 27.09.2014

@author: Simon Gwerder
'''

# from requests.adapters import TimeoutSauce
import requests
import timeit
import datetime

from filter import Filter
import utils
from configloader import ConfigLoader
from thesaurus.rdfgraph import RDFGraph
from translator import Translator

class BaseThesaurus:
    minCount = 5

    pass

# class ConnectionTimeout(TimeoutSauce):
#    def __init__(self, *args, **kwargs):
#        connect = kwargs.get('connect', 5)
#        read = kwargs.get('read', connect)
#        super(ConnectionTimeout, self).__init__(connect=connect, read=read)

# requests.adapters.TimeoutSauce = ConnectionTimeout

# key'r that got too many different meaningless values (key still will be added as concept)

def outputFile(outputName, outputEnding, printDate):
    if printDate:
        dateString = datetime.date.today().isoformat()
        dateString = dateString.replace('-', '')
        dateString = dateString[2:] # substring from incl. 3rd char to end of string
        return utils.dataDir() + outputName + '_' + dateString + outputEnding
    else:
        return utils.dataDir() + outputName + outputEnding


if __name__ == '__main__':

    startTime = timeit.default_timer()

    cl = ConfigLoader()

    tagInfoSortDesc = cl.getTagInfoAPIString('sort_desc')
    tagInfoAllKeys = cl.getTagInfoAPIString('all_keys')
    tagInfoValueOfKey = cl.getTagInfoAPIString('value_of_key')
    tagInfoWikiPageOfKey = cl.getTagInfoAPIString('wiki_page_of_key')
    tagInfoWikiPageOfTag = cl.getTagInfoAPIString('wiki_page_of_tag')
    tagInfoTagPostfix = cl.getTagInfoAPIString('tag_postfix')

    osmWikiBase = cl.getThesaurusString('osm_wiki_page')
    keySchemeName = cl.getThesaurusString('key_scheme_name')
    tagSchemeName = cl.getThesaurusString('tag_scheme_name')

    outputName = cl.getThesaurusString('output_name') # osm_tag_thesaurus
    outputEnding = cl.getThesaurusString('default_format') # .rdf

    translationHintDE = cl.getThesaurusString('translation_hint_DE')
    translationHintEN = cl.getThesaurusString('translation_hint_EN')

    minCount = cl.getThesaurusInt('minimum_count')

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

        r = ''
        for valueItem in valueData:
            if not filterUtil.hasValue(valueItem['value']) and valueItem['in_wiki'] and utils.validCharsCheck(valueItem['value']) and valueItem['count'] >= minCount:
                k = tagMap.get(key)
                if(k is not None):
                    k.append(valueItem['value'])
                    r = r + ',  ' + valueItem['value']
                else:
                    k = [valueItem['value']]
                    r = valueItem['value']
                tagMap[key] = k

        print(str(len(tagMap)) + ' : ' + key + '\t\t' + r)


    graph = RDFGraph()

    keyScheme = graph.addConceptScheme(keySchemeName)
    tagScheme = graph.addConceptScheme(tagSchemeName)

    keyCount = 0;
    tagCount = 0;

    translator = Translator()

    for key in keyList:
        keyCount = keyCount + 1
        keyConcept = graph.addConcept(osmWikiBase + 'Key:' + key)
        graph.addPrefLabel(keyConcept, key)

        graph.addInScheme(keyConcept, keyScheme)
        #graph.addHasTopConcept(keyScheme, keyConcept)

        print(str(keyCount) + '/' + str(len(keyList)) + ' : ' + osmWikiBase + 'Key:' + key)
        valueList = tagMap.get(key)
        if valueList is None:
            continue
        for value in valueList:
            taglink = osmWikiBase + 'Tag:' + key + '=' + value  # before: key + '%3D' + value
            # result = requests.get('http://' + taglink)
            tagWikiPage = requests.get(tagInfoWikiPageOfTag + key + tagInfoTagPostfix + value)
            if len(tagWikiPage.json()) > 0:
                print('\t' + taglink)
                tagWikiPageJson = tagWikiPage.json()
                tagConcept = graph.addConcept(taglink)
                graph.addPrefLabel(tagConcept, key + '=' + value)
                graph.addBroader(tagConcept, keyConcept)
                graph.addNarrower(keyConcept, tagConcept)
                graph.addInScheme(tagConcept, tagScheme)
                tagCount = tagCount + 1

                descriptionDE = ''
                descriptionEN = ''

                for langItems in tagWikiPageJson:

                    if langItems['lang'] == 'de':
                        temp = langItems['description']
                        if temp is not None and not temp == '':
                            descriptionDE = temp
                            print '\t\tde: ' + descriptionDE
                    elif langItems['lang'] == 'en':
                        temp = langItems['description']
                        if  temp is not None and not temp == '':
                            descriptionEN = temp
                            print '\t\ten: ' + descriptionEN

                if descriptionDE == '' and not descriptionEN == '':
                    graph.addScopeNote(tagConcept, descriptionEN, 'en')
                    graph.addScopeNote(tagConcept, translator.translateENtoDE(descriptionEN) + ' ' + translationHintDE, 'de')
                elif not descriptionDE == '' and descriptionEN == '':
                    graph.addScopeNote(tagConcept, translator.translateDEtoEN(descriptionDE) + ' ' + translationHintEN, 'en')
                    graph.addScopeNote(tagConcept, descriptionDE, 'de')
                elif not descriptionDE == '' and not descriptionEN == '':
                    graph.addScopeNote(tagConcept, descriptionEN, 'en')
                    graph.addScopeNote(tagConcept, descriptionDE, 'de')

                imageData = langItems['image']
                depiction = imageData['image_url']
                if depiction is not None and not depiction == '':
                    graph.addDepiction(tagConcept, depiction)
                    print '\t\t' + depiction



    for filteredKey in filterUtil.completeFilterList():
        keyWikiPage = requests.get(tagInfoWikiPageOfKey + filteredKey)
        if len(keyWikiPage.json()) > 0:
            keyConcept = graph.addConcept(osmWikiBase + 'Key:' + filteredKey)
            graph.addPrefLabel(keyConcept, filteredKey)
            graph.addInScheme(keyConcept, keyScheme)
            graph.addHasTopConcept(keyScheme, keyConcept)
            keyCount = keyCount + 1

    graph.serialize(outputFile(outputName, outputEnding, printDate=True))

    print('\n\nKeys: ' + str(keyCount))
    print('Tags: ' + str(tagCount))
    print ('Tripples: ' + str(graph.tripplesCount()))

    stopTime = timeit.default_timer()

print 'Generated in: ' + str((stopTime - startTime) / 60) + ' minutes'
