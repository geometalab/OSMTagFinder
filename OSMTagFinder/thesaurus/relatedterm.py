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
        label = prefLabelEN.decode("utf-8")
        if self.rdfGraph.isInKeyScheme(keyTagConcept):
            label = keyTagConcept.split('Key:')[1]
        else:
            label = keyTagConcept.split('Tag:')[1]
        label = (label.replace('=','_')).decode("utf-8")
        termConcept = self.rdfGraph.addConcept(self.termSchemeName + '/' + label)
        self.rdfGraph.addInScheme(termConcept, self.termSchemeName)
        self.rdfGraph.addPrefLabel(termConcept, prefLabelEN, language='en')
        self.rdfGraph.addPrefLabel(termConcept, prefLabelDE, language='de')
        self.rdfGraph.addRelatedMatch(keyTagConcept, termConcept)
        self.rdfGraph.addRelatedMatch(termConcept, keyTagConcept)
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

    def removeAltLabelLiteral(self, termConcept, altLabelObj):
        self.rdfGraph.removeAltLabelLiteral(termConcept, altLabelObj)

    def removeBroaderLiteral(self, termConcept, broaderObj):
        self.rdfGraph.removeAltLabelLiteral(termConcept, broaderObj)

    def removeNarrowerLiteral(self, termConcept, narrowerObj):
        self.rdfGraph.removeAltLabelLiteral(termConcept, narrowerObj)

    def save(self):
        self.rdfGraph.serialize(self.rdfGraph.filePath)
        return self.rdfGraph.filePath



