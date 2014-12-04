# -*- coding: utf-8 -*-
'''
Created on 02.12.2014

@author: Simon Gwerder
'''

from utilities import utils
from utilities.configloader import ConfigLoader
from thesaurus.rdfgraph import RDFGraph

class Repairer:

    cl = ConfigLoader()

    def __init__(self):
        rdfGraph = RDFGraph(utils.dataDir() + 'tagfinder_thesaurus.rdf')

        keyBaseLink = self.cl.getThesaurusString('KEY_SCHEME_NAME') # http://wiki.openstreetmap.org/wiki/Key
        tagBaseLink = self.cl.getThesaurusString('TAG_SCHEME_NAME') # http://wiki.openstreetmap.org/wiki/Tag
        termBaseLink = self.cl.getThesaurusString('TERM_SCHEME_NAME') # http://wiki.openstreetmap.org/wiki/Term

        for keySubject in rdfGraph.getSubByScheme(keyBaseLink):
            for relMatch in rdfGraph.getRelatedMatch(keySubject):
                if ' ' in str(relMatch):
                    newRelMatch = str(relMatch).replace(' ','_')
                    rdfGraph.removeRelatedMatch(keySubject, relMatch)
                    rdfGraph.addRelatedMatch(keySubject, newRelMatch)
                    print 'Replaced: ' + relMatch + ' with: ' + newRelMatch

        for tagSubject in rdfGraph.getSubByScheme(tagBaseLink):
            for relMatch in rdfGraph.getRelatedMatch(tagSubject):
                if ' ' in str(relMatch):
                    newRelMatch =  str(relMatch).replace(' ','_')
                    rdfGraph.removeRelatedMatch(tagSubject, relMatch)
                    rdfGraph.addRelatedMatch(tagSubject, newRelMatch)
                    print 'Replaced: ' + relMatch + ' with: ' + newRelMatch

        for termSubject in rdfGraph.getSubByScheme(termBaseLink):
            for relMatch in rdfGraph.getRelatedMatch(termSubject):
                isOk = True
                listRelMatchOfSubj = utils.genToList(rdfGraph.getRelatedMatch(relMatch))
                for isItMe in listRelMatchOfSubj:
                    if isItMe is termSubject:
                        isOk = True
                        break
                    isOk = False
                if not isOk:
                    print 'Error: ' + termSubject + ' and ' + relMatch

        rdfGraph.serialize(rdfGraph.filePath)

if __name__ == '__main__':
    Repairer()








