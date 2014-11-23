# -*- coding: utf-8 -*-
'''
Created on 16.11.2014

@author: Simon Gwerder
'''

from utilities.configloader import ConfigLoader
from rdfgraph import RDFGraph

class RelatedTerm:

    rdfGraph = RDFGraph()
    cl = ConfigLoader()

    termSchemeName = cl.getThesaurusString('TERM_SCHEME_NAME')
    termSchemeTitle = cl.getThesaurusString('TERM_SCHEME_TITLE')
    creator = cl.getThesaurusString('CREATOR')

    termScheme = None

    def __init__(self, rdfGraph):
        if rdfGraph is not None:
            self.rdfGraph = rdfGraph

        self.termScheme = self.rdfGraph.addConceptScheme(self.termSchemeName, self.termSchemeTitle, self.creator) # doesn't matter if called a lot

    def createTerm(self, keyTagConcept, prefLabelEN, prefLabelDE):
        termConcept = self.rdfGraph.addConcept(self.termSchemeName + '/' + prefLabelEN.decode("utf-8"))
        self.rdfGraph.addInScheme(termConcept, self.termSchemeName)
        self.rdfGraph.addPrefLabel(termConcept, prefLabelEN, language='en')
        self.rdfGraph.addPrefLabel(termConcept, prefLabelDE, language='de')
        self.rdfGraph.addRelatedMatch(keyTagConcept, termConcept)
        self.rdfGraph.addRelatedMatch(termConcept, keyTagConcept)
        #TODO if is tag => add broader narrower to key term equivalent
        return termConcept

    def addAltLabelEN(self, termConcept, altLabelEN):
        self.rdfGraph.addAltLabel(termConcept, altLabelEN, 'en')
        return termConcept

    def addAltLabelDE(self, termConcept, altLabelDE):
        self.rdfGraph.addAltLabel(termConcept, altLabelDE, 'de')
        return termConcept

    def addNarrowerLiteralEN(self, termConcept, narrowerEN):
        self.rdfGraph.addNarrowerLiteral(termConcept, narrowerEN, 'en')
        return termConcept

    def addNarrowerLiteralDE(self, termConcept, narrowerDE):
        self.rdfGraph.addNarrowerLiteral(termConcept, narrowerDE, 'de')
        return termConcept

    def addBroaderLiteralEN(self, termConcept, broaderEN):
        self.rdfGraph.addBroaderLiteral(termConcept, broaderEN, 'en')
        return termConcept

    def addBroaderLiteralDE(self, termConcept, broaderDE):
        self.rdfGraph.addBroaderLiteral(termConcept, broaderDE, 'de')
        return termConcept

    def save(self):
        self.rdfGraph.serialize(self.rdfGraph.filePath)
        return self.rdfGraph.filePath



