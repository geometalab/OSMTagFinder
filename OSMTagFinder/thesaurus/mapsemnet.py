# -*- coding: utf-8 -*-
'''
Created on 08.11.2014

@author: Simon Gwerder
'''

from rdflib.namespace import SKOS

from thesaurus.rdfgraph import RDFGraph
from utilities import utils
from utilities.configloader import ConfigLoader
from externalapi.osmsemanticnet import OSMSemanitcNet

class MapOSMSemanticNet:

    def __init__(self, tagFinderFilePath, osnSemNetFilePath=None):

        print('Loading TagFinder graph')
        tagFinderRDF = RDFGraph(tagFinderFilePath)
        osnSemNetRDF = None
        if osnSemNetFilePath is not None:
            print('Loading OSN graph')
            osnSemNetRDF = RDFGraph(osnSemNetFilePath)
        osn = OSMSemanitcNet(osnSemNetRDF) # if osnSemNetRDF is None it will check the web graph

        termSchemeName = ConfigLoader().getThesaurusString('TERM_SCHEME_NAME')

        count = 0;
        for subject, predicate, obj in tagFinderRDF.graph:
            if not osn.baseUrl in subject and not termSchemeName in subject: # check if some osn matches have been added already
                osnConcept = None
                if predicate == SKOS.prefLabel:
                    count = count + 1
                    if '=' in str(obj):
                        splitArray = str(obj).split('=')
                        osnConcept = osn.getConcept(splitArray[0], splitArray[1])
                    else:
                        osnConcept = osn.getConcept(str(obj))

                if osnConcept:
                    tagFinderRDF.addRelatedMatch(subject, osnConcept)
                    print(str(count) + ' : Added Matching Concept Mapping from: ' + subject + '\t\t\tto: ' + osnConcept)

        tagFinderRDF.serialize(tagFinderFilePath)


if __name__ == '__main__':

    tagFinderFilePath = utils.dataDir() + 'tagfinder_thesaurus.rdf'
    osnSemNetFilePath = utils.semnetDir() + 'osm_semantic_network.rdf'

    MapOSMSemanticNet(tagFinderFilePath, osnSemNetFilePath)




