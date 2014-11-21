# -*- coding: utf-8 -*-
'''
Created on 16.11.2014

@author: Simon Gwerder
'''

from utilities.configloader import ConfigLoader
from relatedterm import RelatedTerm

class EditTerms:

    cl = ConfigLoader()
    keySchemeName = cl.getThesaurusString('KEY_SCHEME_NAME')
    noTermNote = cl.getThesaurusString('NO_TERM')
    savePointNote = cl.getThesaurusString('SAVE_POINT')

    __savePoint = None
    __currentRelTerm = None

    relatedTerm = None
    editStack = []

    def __init__(self, rdfGraph):
        self.relatedTerm = RelatedTerm(rdfGraph)
        self.editStack = self.__getEditConceptList()

    def hasNext(self):
        return len(self.editStack) > 0

    def getNext(self):
        if self.hasNext():
            if self.__savePoint is not None: # savePoint still on old position
                self.removeLastPosNote(self.__savePoint)
            nextSubject = self.editStack[0]
            self.editStack.remove(nextSubject)
            self.__savePoint = nextSubject # advancing savePoint to first element in list (top of stack)
            self.addLastPosNote(nextSubject) # give note to new savePoint
            return nextSubject
        return None

    def __getKeyConceptList(self):
        keyConcepts = self.relatedTerm.rdfGraph.getSubByScheme(self.keySchemeName)
        retList = []
        #if len(list(keyConcepts)) > 0:
        for keyConcept in keyConcepts:
            editNote = self.relatedTerm.rdfGraph.getEditorialNote(keyConcept)
            if editNote is not None and editNote == self.savePointNote:
                self.__savePoint = keyConcept
            elif editNote is not None and editNote == self.noTermNote:
                retList.append(keyConcept)
        return retList

    def __getEditConceptList(self):
        retList = []
        keyConcepts = self.__getKeyConceptList()
        for keyConcept in keyConcepts:
            retList.append(keyConcept)
            tagConcepts = self.relatedTerm.rdfGraph.getNarrower(keyConcept)
            #if len(list(tagConcepts)) > 0:
            for tagConcept in tagConcepts:
                editNote = self.relatedTerm.rdfGraph.getEditorialNote(tagConcept)
                if editNote is not None and editNote == self.savePointNote:
                    self.__savePoint = tagConcept
                elif editNote is not None and editNote == self.noTermNote:
                    retList.append(tagConcept)
        if self.__savePoint is not None:
            retList.insert(0, self.__savePoint) # add last editing position to the beginning of the list
        return retList

    def removeLastPosNote(self, keyTagConcept):
        self.relatedTerm.rdfGraph.removeEditorialNote(keyTagConcept, self.savePointNote) # doesnt matter if notes do not exist

    def removeNoTermNote(self, keyTagConcept):
        self.relatedTerm.rdfGraph.removeEditorialNote(keyTagConcept, self.noTermNote) # doesnt matter if notes do not exist

    def addLastPosNote(self, keyTagConcept):
        self.relatedTerm.rdfGraph.addEditorialNote(keyTagConcept, self.savePointNote)

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

    def save(self):
        return self.relatedTerm.save()





