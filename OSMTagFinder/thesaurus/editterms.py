# -*- coding: utf-8 -*-
'''
Created on 16.11.2014

@author: Simon Gwerder
'''

from utilities.configloader import ConfigLoader
from relatedterm import RelatedTerm
from rdfgraph import RDFGraph

class EditTerms:

    rdfGraph = RDFGraph()
    cl = ConfigLoader()
    keySchemeName = cl.getThesaurusString('KEY_SCHEME_NAME')
    noTermNote = cl.getThesaurusString('NO_TERM')
    lastPosNote = cl.getThesaurusString('LAST_POSITION')

    __lastPosition = None
    __currentRelTerm = None

    relatedTerm = None
    editStack = None

    def __init__(self, rdfGraph):
        if rdfGraph is not None:
            self.rdfGraph = rdfGraph
        self.relatedTerm = RelatedTerm(self.rdfGraph)
        self.editStack = list(reversed( self.__getEditConceptList() )) # reversing the list, because we want to use it as a stack

    def hasNext(self):
        return len(self.editStack) > 0

    def getNext(self):
        if self.hasNext():
            if self.__lastPosition is not None: # last pos still on old position
                self.removeLastPosNote(str(self.__lastPosition))
            nextSubject = self.editStack.pop()
            self.__lastPosition = self.editStack[-1] # advancing last position to last element in list (top of stack)
            self.addLastPosNote(str(self.__lastPosition)) # give not to new last pos
            return nextSubject
        return None

    def __getKeyConceptList(self):
        keyConcepts = self.rdfGraph.getSubByScheme(self.keySchemeName)
        retList = []
        #if len(list(keyConcepts)) > 0:
        for keyConcept in keyConcepts:
            editNote = self.rdfGraph.getEditorialNote(keyConcept)
            if editNote is not None and editNote == self.lastPosNote:
                self.__lastPosition = keyConcept
            elif editNote is not None and editNote == self.noTermNote:
                retList.append(keyConcept)
        return retList

    def __getEditConceptList(self):
        retList = []
        keyConcepts = self.__getKeyConceptList()
        for keyConcept in keyConcepts:
            retList.append(keyConcept)
            tagConcepts = self.rdfGraph.getNarrower(keyConcept)
            #if len(list(tagConcepts)) > 0:
            for tagConcept in tagConcepts:
                editNote = self.rdfGraph.getEditorialNote(tagConcept)
                if editNote is not None and editNote == self.lastPosNote:
                    self.__lastPosition = tagConcept
                elif editNote is not None and editNote == self.noTermNote:
                    retList.append(tagConcept)
        if self.__lastPosition is not None:
            retList.insert(0, self.__lastPosition) # add last editing position to the beginning of the list
        return retList

    def removeLastPosNote(self, keyTagConcept):
        self.rdfGraph.removeEditorialNote(keyTagConcept, self.lastPosNote) # doesnt matter if notes do not exist

    def removeNoTermNote(self, keyTagConcept):
        self.rdfGraph.removeEditorialNote(keyTagConcept, self.noTermNote) # doesnt matter if notes do not exist

    def addLastPosNote(self, keyTagConcept):
        self.rdfGraph.addEditorialNote(keyTagConcept, self.lastPosNote)

    def createTerm(self, keyTagConcept, prefLabelEN, prefLabelDE):
        self.removeNoTermNote(keyTagConcept)
        self.__currentRelTerm = self.relatedTerm.createTerm(keyTagConcept, prefLabelEN, prefLabelDE)

    def addAltLabelEN(self, altLabelEN):
        if self.__currentRelTerm is not None and altLabelEN is not None and len(altLabelEN) > 0:
            self.relatedTerm.addAltLabelEN(self.__currentRelTerm, altLabelEN)

    def addAltLabelDE(self, altLabelDE):
        if self.__currentRelTerm is not None and altLabelDE is not None and len(altLabelDE) > 0:
            self.relatedTerm.addAltLabelDE(self.__currentRelTerm, altLabelDE)

    def addNarrowerLiteralEN(self, narrowerEN):
        if self.__currentRelTerm is not None and narrowerEN is not None and len(narrowerEN) > 0:
            self.relatedTerm.addNarrowerLiteralEN(self.__currentRelTerm, narrowerEN)

    def addNarrowerLiteralDE(self, narrowerDE):
        if self.__currentRelTerm is not None and narrowerDE is not None and len(narrowerDE) > 0:
            self.relatedTerm.addNarrowerLiteralDE(self.__currentRelTerm, narrowerDE)

    def addBroaderLiteralEN(self, broaderEN):
        if self.__currentRelTerm is not None and broaderEN is not None and len(broaderEN) > 0:
            self.relatedTerm.addBroaderLiteralEN(self.__currentRelTerm, broaderEN)

    def addBroaderLiteralDE(self, broaderDE):
        if self.__currentRelTerm is not None and broaderDE is not None and len(broaderDE) > 0:
            self.relatedTerm.addBroaderLiteralDE(self.__currentRelTerm, broaderDE)






