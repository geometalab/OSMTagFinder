# -*- coding: utf-8 -*-
'''
Created on 27.09.2014

@author: Simon Gwerder
'''

import requests
import re
import timeit
#from requests.adapters import TimeoutSauce


from thesaurus.skosgraph import SkosGraph

#class ConnectionTimeout(TimeoutSauce):
#    def __init__(self, *args, **kwargs):
#        connect = kwargs.get('connect', 5)
#        read = kwargs.get('read', connect)
#        super(ConnectionTimeout, self).__init__(connect=connect, read=read)

#requests.adapters.TimeoutSauce = ConnectionTimeout

#key's that got too many different meaningless values (key still will be added as concept)
exactKeyFilter = ['name', 'ele', 'comment', 'image', 'symbol', 'deanery', 'jel', 'rating', 'school:FR', 'alt','is_in', 'url', 'website',
                  'wikipedia','email', 'converted_by','phone','information','opening_hours','date','time','collection_times',
                  'colour','fee', 'population','access','noexit','towards','bus_routes','busline','lines', 'type','denotation',
                  'CONTINUE','continue','copyright','stop', 'network', 'comment', 'old_name', 'destination', 'brand',
                  'turn:lanes', 'owner', 'fire_hydrant:city', 'fire_hydrant:street', 'country', 'contact:google_plus',
                  'short_name:ru', 'tpuk_ref', 'wikimedia_commons', 'operator', 'source', 'wikipedia', 'railway:etcs',
                  'de:regionalschluessel', 'de:amtlicher_gemeindeschluessel', 'contact:xing', 'nspn', '_picture_',
                  '_waypoint_', 'label', 'branch', 'note', 'phone', 'created_by', 'start_date', 'end_date', 'description', 'description:ru']

prefixKeyFilter = ['name:', 'note:', 'alt_name', 'int_name', 'loc_name', 'not:name', 'nat_name', 'official_name', 'short_name', 'reg_name', 'sorting_name',
                   'contact:', 'addr', 'icao', 'iata' 'onkz', 'is_in', 'fixme', 'seamark:fixme',
                   'ois:fixme', 'todo', 'type:', 'admin_level', 'AND_', 'AND:', 'seamark:', 'attribution', 'openGeoDB', 'ref', 'source_ref', 'tiger',
                    'yh:', 'ngbe:', 'gvr:code','old_ref_legislative', 'sl_stop_id', 'ele:', 'source:',
                   'osak:', 'kms', 'gnis:', 'nhd', 'chicago:building_id', 'hgv', 'nhs', 'ncat', 'nhd-shp:', 'osmc:', 'kp',
                   'int_name', 'CLC:', 'naptan:', 'building:ruian:', 'massgis:', 'WroclawGIS:', 'ref:FR:FANTOIR', 'rednap:', 'ts_', 'type:FR:FINESS',
                   'route_ref', 'lcn_ref', 'ncn_ref', 'rcn', 'rwn_ref', 'old_ref', 'prow_ref', 'local_ref', 'loc_ref', 'reg_ref', 'url',
                   'nat_ref', 'int_ref', 'uic_ref', 'asset_ref', 'carriageway_ref', 'junction:ref', 'fhrs:', 'osmc:', 'cep', 'protection_title',
                   'bag:extract', 'ref:bagid', 'adr_les', 'bag:', 'fresno_', 'uuid', 'uic_name', 'gtfs_id', 'USGS-LULC:', 'reg_', 'IBGE:',
                   'sagns_id', 'protect_id', 'PMSA_ref', 'destination:', 'EH_ref', 'rtc_rate', 'cyclestreets_id', 'woeid', 'CEMT',
                   'depth:dredged']

valueFilter = []
minCount = 5

def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def validCheck(s):
    if contains_digits(s):
        return False
    if ' ' in s:
        return False
    if ';' in s:
        return False
    return True

_digits = re.compile('\d')
def contains_digits(d):
    return bool(_digits.search(d))

def startsWithFilter(strKey, filterList):
    for prefixKeyFilter in filterList:
        lowStrKey = strKey.lower()
        lowKeyFilter = prefixKeyFilter.lower()
        if(lowStrKey.startswith(lowKeyFilter)):
            return True
    return False


if __name__ == '__main__':

    startTime = timeit.default_timer()

    tagInfoSortDesc = '&sortname=count_all&sortorder=desc'
    tagInfoAllKeys = 'http://taginfo.osm.org/api/4/keys/all?filter=in_wiki'
    tagInfoValueOfKey = 'http://taginfo.osm.org/api/4/key/values?key='
    tagInfoWikiPageOfKey = 'http://taginfo.osm.org/api/4/key/wiki_pages?key='
    tagInfoWikiPageOfTag = 'http://taginfo.osm.org/api/4/tag/wiki_pages?key=' # + &value=blabla
    osmWikiBase = 'http://wiki.openstreetmap.org/wiki/'
    osmSchemeName = 'http://wiki.openstreetmap.org/wiki/Tag'
    outputfile = './data/osm_tag_thesaurus_v0.2.rdf'

    keyResult = requests.get(tagInfoAllKeys + tagInfoSortDesc);
    keyJson = keyResult.json();
    keyData = keyJson['data'];

    keyCount = 0
    keyList = []
    for keyItem in keyData:
        if keyItem['count_all'] < minCount:
            break; #speedup because of sorted list
        if keyItem['key'] not in exactKeyFilter and not startsWithFilter(keyItem['key'], prefixKeyFilter) and validCheck(keyItem['key']) and keyItem['values_all'] >= minCount:
            #keyWikiPage = requests.get(tagInfoWikiPageOfKey + keyItem['key'].replace('%',''))
            #if(len(keyWikiPage.json()) > 0):
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
            if valueItem['value'] not in valueFilter and valueItem['in_wiki'] and validCheck(valueItem['value']) and valueItem['count'] >= minCount:
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

        print(str(keyCount) + '/' + str(len(keyList)) + ' : ' +  osmWikiBase + 'Key:' + key)
        valueList = tagMap.get(key)
        if valueList is None:
            continue
        for value in valueList:
            taglink = osmWikiBase + 'Tag:' + key + '=' + value #before: key + '%3D' + value
            #result = requests.get('http://' + taglink)
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
    for filteredKey in prefixKeyFilter:
        keyWikiPage = requests.get(tagInfoWikiPageOfKey + filteredKey)
        if len(keyWikiPage.json()) > 0:
            keyConcept = graph.addConcept(osmWikiBase + 'Key:' + filteredKey)
            graph.addPrefLabel(keyConcept, filteredKey, 'de')
            graph.addInScheme(keyConcept, scheme)
            graph.addHasTopConcept(scheme, keyConcept)
            keyCount = keyCount + 1

    ser = graph.serialize(outputfile)
    print(ser)

    print('\n\nKeys: ' + str(keyCount))
    print('Tags: ' + str(tagCount))

    stopTime = timeit.default_timer()

print 'Generated in: ' + str((stopTime - startTime) / 60) + ' minutes'
