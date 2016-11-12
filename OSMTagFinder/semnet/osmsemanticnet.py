# -*- coding: utf-8 -*-
'''
Created on 08.11.2014

@author: Simon Gwerder
'''

import requests
from rdflib import Literal
from rdflib.namespace import SKOS
from utilities import utils
from utilities.configloader import ConfigLoader


class OSMSemanticNet:

    cl = ConfigLoader()
    baseUrl = cl.getThesaurusString('OSM_SEM_NET')
    suffix = cl.getThesaurusString('OSM_SEM_NET_SUFFIX')

    osnRdfGraph = None

    def __init__(self, osnRDFGraph=None):
        if osnRDFGraph is not None:
            self.osnRdfGraph = osnRDFGraph


    def getConceptWeb(self, key, value=None):
        if value is None:
            callStr = self.baseUrl + key
        else:
            callStr = self.baseUrl + key + self.suffix + value
        try:
            response = requests.get(callStr)
            if response.status_code < 400:
                return callStr
        except requests.exceptions.Timeout:
            return None
        return None

    def getConceptGraph(self, key, value=None):
        literal = ''
        if value is not None:
            literal = Literal(key + '=' + value, lang='en')
        else:
            literal = Literal('k_' + key, lang='en')
        genSubjects = self.osnRdfGraph.graph.subjects(SKOS.altLabel, literal)
        return utils.genGetFirstItem(genSubjects)

    def getConcept(self, key, value=None):
        if self.osnRdfGraph is None:
            return self.getConceptWeb(key, value)
        else:
            return self.getConceptGraph(key, value)


