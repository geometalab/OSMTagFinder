# -*- coding: utf-8 -*-
'''
Created on 16.11.2014

@author: Simon Gwerder
'''

import operator

from utilities import utils
from utilities.configloader import ConfigLoader

from relatedterm import RelatedTerm


class UpdateTerm:

    cl = ConfigLoader()
    keySchemeName = cl.getThesaurusString('KEY_SCHEME_NAME')
    termSchemeName = cl.getThesaurusString('TERM_SCHEME_NAME')
    noTermNote = cl.getThesaurusString('NO_TERM')
    savePointNote = cl.getThesaurusString('SAVE_POINT')

    __savePoint = None
    __currentRelTerm = None

    relatedTerm = None
    editStack = []

    def __init__(self, rdfGraph):
        self.relatedTerm = RelatedTerm(rdfGraph)
        self.editStack = self.__getEditConceptList()
        savePointConcept = self.relatedTerm.rdfGraph.getSubByEditNote(self.savePointNote)
        if savePointConcept is not None:
            self.__savePoint = savePointConcept
            self.editStack.insert(0, self.__savePoint) # add savePoint to the beginning of the list

    def hasNext(self):
        return len(self.editStack) > 0

    def getNext(self):
        if self.hasNext():
            if self.__savePoint is not None: # savePoint still on old position
                self.removeSavePointNote(self.__savePoint)
            nextSubject = self.editStack[0]
            self.editStack.remove(nextSubject)
            self.__savePoint = nextSubject # advancing savePoint to first element in list (top of stack)
            self.addLastPosNote(nextSubject) # give note to new savePoint
            return nextSubject
        return None

    def sortByStats(self, keyConcepts):
        keyStatsDict = { }
        default = { 'count' : '0', 'use' : 'False' }
        for keyConcept in keyConcepts:
            nodeCount = int((utils.genJsonToDict(self.relatedTerm.rdfGraph.getOSMNode(keyConcept), default))['count'])
            wayCount = int((utils.genJsonToDict(self.relatedTerm.rdfGraph.getOSMWay(keyConcept), default))['count'])
            areaCount = int((utils.genJsonToDict(self.relatedTerm.rdfGraph.getOSMArea(keyConcept), default))['count'])
            relationCount = int((utils.genJsonToDict(self.relatedTerm.rdfGraph.getOSMRelation(keyConcept), default))['count'])
            totalCount = nodeCount + wayCount + areaCount + relationCount
            keyStatsDict[keyConcept] = totalCount
        keyStatsDict = sorted(keyStatsDict.items(), reverse=True, key=operator.itemgetter(1))
        return [i[0] for i in keyStatsDict]

    def __getEditConceptList(self):
        retList = []
        keyConcepts = self.relatedTerm.rdfGraph.getSubByScheme(self.keySchemeName)
        keyConcepts = self.sortByStats(keyConcepts)
        for keyConcept in keyConcepts:
            editNote = self.relatedTerm.rdfGraph.getEditorialNote(keyConcept)
            if editNote is not None and str(editNote) == str(self.noTermNote):
                retList.append(keyConcept)
            tagConcepts = self.relatedTerm.rdfGraph.getNarrower(keyConcept)
            #if len(list(tagConcepts)) > 0:
            for tagConcept in tagConcepts:
                editNote = self.relatedTerm.rdfGraph.getEditorialNote(tagConcept)
                if editNote is not None and str(editNote) == str(self.noTermNote):
                    retList.append(tagConcept)
        return retList

    def removeDuplicates(self, relTermSubject):
        altLabelList = utils.genToList(self.relatedTerm.rdfGraph.getAltLabel(relTermSubject))
        broaderList = utils.genToList(self.relatedTerm.rdfGraph.getBroader(relTermSubject))
        narrowerList = utils.genToList(self.relatedTerm.rdfGraph.getNarrower(relTermSubject))
        for altLabel in altLabelList:
            if altLabel in broaderList or altLabel in narrowerList:
                self.relatedTerm.removeAltLabelLiteral(relTermSubject, altLabel)
        for narrower in narrowerList:
            if narrower in broaderList:
                self.relatedTerm.removeNarrowerLiteral(relTermSubject, narrower)

    def manageNarrowerRelations(self, relTermSubject, keySubject):
        keysNarrowerList = utils.genToList(self.relatedTerm.rdfGraph.getNarrower(keySubject))
        thisPrefLabelList = utils.genToList(self.relatedTerm.rdfGraph.getPrefLabel(relTermSubject))
        for narrowerTag in keysNarrowerList: # is a tag, not a key
            relTermsOfNarrower = utils.genToList(self.relatedTerm.rdfGraph.getRelatedMatch(narrowerTag))
            for narrowerRelTerm in relTermsOfNarrower:
                if self.relatedTerm.rdfGraph.isInTermScheme(narrowerRelTerm) and not narrowerRelTerm == relTermSubject:
                    prefLabelList = utils.genToList(self.relatedTerm.rdfGraph.getPrefLabel(narrowerRelTerm))
                    altLabelList = utils.genToList(self.relatedTerm.rdfGraph.getAltLabel(narrowerRelTerm))
                    for prefLabel in prefLabelList:  # adding those to narrower
                        if prefLabel.language == 'en' and prefLabel not in thisPrefLabelList:
                            self.relatedTerm.addNarrowerLiteralEN(relTermSubject, str(prefLabel))
                        elif prefLabel.language == 'de' and prefLabel not in thisPrefLabelList:
                            self.relatedTerm.addNarrowerLiteralDE(relTermSubject, str(prefLabel))
                    for altLabel in altLabelList:  # adding those to narrower
                        if altLabel.language == 'en' and altLabel not in thisPrefLabelList:
                            self.relatedTerm.addNarrowerLiteralEN(relTermSubject, str(altLabel))
                        elif altLabel.language == 'de' and altLabel not in thisPrefLabelList:
                            self.relatedTerm.addNarrowerLiteralDE(relTermSubject, str(altLabel))

    def manageBroaderRelations(self, relTermSubject, tagSubject):
        tagsBroaderList = utils.genToList(self.relatedTerm.rdfGraph.getBroader(tagSubject))
        thisPrefLabelList = utils.genToList(self.relatedTerm.rdfGraph.getPrefLabel(relTermSubject))
        for broaderKey in tagsBroaderList: # is a key, not a tag, and actually just one
            relTermsOfBroader = utils.genToList(self.relatedTerm.rdfGraph.getRelatedMatch(broaderKey))
            for broaderRelTerm in relTermsOfBroader:
                if self.relatedTerm.rdfGraph.isInTermScheme(broaderRelTerm) and not broaderRelTerm == relTermSubject:
                    prefLabelList = utils.genToList(self.relatedTerm.rdfGraph.getPrefLabel(broaderRelTerm))
                    altLabelList = utils.genToList(self.relatedTerm.rdfGraph.getAltLabel(broaderRelTerm))
                    for prefLabel in prefLabelList:  # adding those to broader
                        if prefLabel.language == 'en' and prefLabel not in thisPrefLabelList:
                            self.relatedTerm.addBroaderLiteralEN(relTermSubject, str(prefLabel))
                        elif prefLabel.language == 'de' and prefLabel not in thisPrefLabelList:
                            self.relatedTerm.addBroaderLiteralDE(relTermSubject, str(prefLabel))
                    for altLabel in altLabelList:  # adding those to broader
                        if altLabel.language == 'en' and altLabel not in thisPrefLabelList:
                            self.relatedTerm.addBroaderLiteralEN(relTermSubject, str(altLabel))
                        elif altLabel.language == 'de' and altLabel not in thisPrefLabelList:
                            self.relatedTerm.addBroaderLiteralDE(relTermSubject, str(altLabel))

    def manageRelations(self, relTermSubject):
        keyTagSubjectList = utils.genToList(self.relatedTerm.rdfGraph.getRelatedMatch(relTermSubject))
        for keyTagSubject in keyTagSubjectList: # will just be one most of times
            if self.relatedTerm.rdfGraph.isInKeyScheme(keyTagSubject): # if is key
                self.manageNarrowerRelations(relTermSubject, keyTagSubject)
            elif self.relatedTerm.rdfGraph.isInTagScheme(keyTagSubject): # else if its tag
                self.manageBroaderRelations(relTermSubject, keyTagSubject)

    def finalize(self):
        relTermGen = self.relatedTerm.rdfGraph.getSubByScheme(self.termSchemeName)
        relTermList = utils.genToList(relTermGen)
        for relTermSubject in relTermList:
            self.manageRelations(relTermSubject)
            self.removeDuplicates(relTermSubject)
        return self.save()

    def removeSavePointNote(self, keyTagSubject):
        self.relatedTerm.rdfGraph.removeEditorialNote(keyTagSubject, self.savePointNote) # doesnt matter if notes do not exist

    def removeNoTermNote(self, keyTagSubject):
        self.relatedTerm.rdfGraph.removeEditorialNote(keyTagSubject, self.noTermNote) # doesnt matter if notes do not exist

    def addLastPosNote(self, keyTagSubject):
        self.relatedTerm.rdfGraph.addEditorialNote(keyTagSubject, self.savePointNote)

    def createTerm(self, keyTagSubject, prefLabelEN, prefLabelDE):
        self.removeNoTermNote(keyTagSubject)
        self.__currentRelTerm = self.relatedTerm.createTerm(keyTagSubject, prefLabelEN, prefLabelDE)

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





