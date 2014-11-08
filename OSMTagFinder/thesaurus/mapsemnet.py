# -*- coding: utf-8 -*-
'''
Created on 08.11.2014

@author: Simon Gwerder
'''

from rdflib.namespace import SKOS

from thesaurus.rdfgraph import RDFGraph
from utilities import utils
from externalapi.osmsemanticnet import OSMSemanitcNet

class MapOSMSemanticNet:

    def __init__(self, tagFinderFilePath, osnSemNetFilePath=None):
        tagFinderRDF = RDFGraph(tagFinderFilePath)
        osnSemNetRDF = None
        if osnSemNetFilePath is not None:
            osnSemNetRDF = RDFGraph(osnSemNetRDF)
        osn = OSMSemanitcNet(osnSemNetRDF)
        count = 0;
        for subject, predicate, obj in tagFinderRDF.graph:
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

    osnSemNetFilePath = utils.dataDir() + 'semnet\osm_semantic_network.rdf'
    tagFinderFilePath = utils.dataDir() + 'osm_tag_thesaurus_141107.rdf'

    MapOSMSemanticNet(osnSemNetFilePath, tagFinderFilePath)




