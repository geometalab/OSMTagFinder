# -*- coding: utf-8 -*-
'''
Created on 06.12.2014

@author: Simon Gwerder
'''

from utilities import utils
from test.idpresettest import IDPresetsSetup
from rdfgraph import RDFGraph
from utilities.configloader import ConfigLoader
import re

if __name__ == '__main__':
    setup = IDPresetsSetup(utils.testDir() + 'presets.json')

    cl = ConfigLoader()

    keySchemeName = cl.getThesaurusString('KEY_SCHEME_NAME')
    tagSchemeName = cl.getThesaurusString('TAG_SCHEME_NAME')
    termSchemeName = cl.getThesaurusString('TERM_SCHEME_NAME')

    outputName = cl.getThesaurusString('OUTPUT_NAME')
    outputEnding = cl.getThesaurusString('DEFAULT_FORMAT')
    rdfGraph = RDFGraph(utils.outputFile(utils.dataDir(), outputName, outputEnding, useDateEnding=False))

    badChars = re.compile('[^ =".,:;/\?\(\)\]\[\!\*]')
    def getGoodName(currentName):
        return badChars.sub(currentName, '_')

    def getRelatedTerm(relMatchList):
        if relMatchList is None or len(relMatchList) <= 0:
            for relMatch in relMatchList:
                if rdfGraph.isInTermScheme(relMatch):
                    return relMatch
        return None

    def save():
        rdfGraph.serialize(rdfGraph.filePath)

    def termAddPrefLabelEN(termConcept, prefLabelEN):
        if prefLabelEN is None: return
        rdfGraph.addPrefLabel(termConcept, prefLabelEN, language='en')

    def termAddPrefLabelDE(termConcept, prefLabelDE):
        if prefLabelDE is None: return
        rdfGraph.addPrefLabel(termConcept, prefLabelDE, language='de')

    def termAddRelationEN(termConcept, termEN, rbn):
        if termEN is None: return
        if rbn == 'r':
            rdfGraph.addAltLabel(termConcept, termEN, language='en')
        elif rbn == 'b':
            rdfGraph.addBroaderLiteral(termConcept, termEN, language='en')
        elif rbn == 'n':
            rdfGraph.addNarrowerLiteral(termConcept, termEN, language='en')
        elif rbn == '\\save':
            save()
            termAddRelationEN(termConcept, termEN, readLine('>'))

    def termAddRelationDE(termConcept, termDE, rbn):
        if termDE is None: return
        if rbn == 'r':
            rdfGraph.addAltLabel(termConcept, termDE, language='de')
        elif rbn == 'b':
            rdfGraph.addBroaderLiteral(termConcept, termDE, language='de')
        elif rbn == 'n':
            rdfGraph.addNarrowerLiteral(termConcept, termDE, language='de')
        if termDE == '\\save':
            save()
            termAddRelationDE(termConcept, termDE, readLine('>'))

    def createTerm(keyTagConcept, name):
        termConcept = rdfGraph.addConcept(termSchemeName + '/' + name.decode("utf-8"))
        rdfGraph.addInScheme(termConcept, termSchemeName)
        rdfGraph.addRelatedMatch(keyTagConcept, termConcept)
        rdfGraph.addRelatedMatch(termConcept, keyTagConcept)
        return termConcept

    def readLine(prefix='>'):
        rawData = raw_input(prefix)
        return utils.encode(rawData)

    current = 0
    for idPreset in setup.getIDPresets():
        if not current >= 0:
            current = current + 1
            continue
        relTermToAddTo = None

        for tag in idPreset.tags:
            key = tag.split('=')[0]
            value = tag.split('=')[1]

            if '*' in value: # is key
                keySubject = keySchemeName + ':' + key
                prefLabel = utils.genGetFirstItem(rdfGraph.getPrefLabel(str(keySubject)))
                if prefLabel is not None: # key exists
                    relMatchList = utils.genToList(rdfGraph.getRelatedMatch(str(keySubject)))
                    foundRelTerm = getRelatedTerm(relMatchList)
                    if foundRelTerm is not None:
                        relTermToAddTo = foundRelTerm
                    else:
                        relName = getGoodName(key)
                        relTermToAddTo = createTerm(keySubject, relName)

            else: # is tag
                tagSubject = tagSchemeName + ':' + key + '=' + value
                prefLabel = utils.genGetFirstItem(rdfGraph.getPrefLabel(str(tagSubject)))
                if prefLabel is not None: # tag exists
                    relMatchList = utils.genToList(rdfGraph.getRelatedMatch(str(tagSubject)))
                    foundRelTerm = getRelatedTerm(relMatchList)
                    if foundRelTerm is not None:
                        relTermToAddTo = foundRelTerm
                    else:
                        relName = getGoodName(key + '_' + value)
                        relTermToAddTo = createTerm(tagSubject, relName)

            if relTermToAddTo is not None:
                print '\n\n' + str(current) + '/' + str(len(setup.getIDPresets())) + ' @ idTag: ' + tag + ', relTerm: ' + relTermToAddTo
                print '=' * 100
                prefLabelEN = (idPreset.name).lower()
                print 'PrefLabel EN: ' + prefLabelEN
                prefLabelDE = readLine(prefix='PrefLabel DE: ')
                print 'PrefLabel DE: ' + prefLabelDE + '\n'
                termAddPrefLabelEN(relTermToAddTo, prefLabelEN)
                termAddPrefLabelDE(relTermToAddTo, prefLabelDE)

                for term in idPreset.terms:
                    term = term.lower()
                    if term == prefLabelEN: continue
                    rbn = readLine(prefix='Add EN term: ' + term + ' to (r), (b), (n): ')
                    termAddRelationEN(relTermToAddTo, term, rbn)
                    termDE = readLine(prefix='Add DE equivalent: ')
                    termAddRelationDE(relTermToAddTo, termDE, rbn)

        current = current + 1
    save()

