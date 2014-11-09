# -*- coding: utf-8 -*-
'''
Created on 26.09.2014

@author: Simon Gwerder
'''

from rdflib import Graph, Literal, Namespace, RDF, URIRef, plugin, XSD
from rdflib.namespace import SKOS
from rdflib.namespace import FOAF
from rdflib.serializer import Serializer
from rdflib.util import guess_format
from utilities import utils
from utilities.configloader import ConfigLoader

# from skosserializer import SKOSSerializer

class RDFGraph:
    encoding = 'utf-8'
    graph = Graph()

    cl = ConfigLoader()

    foaf = Namespace("http://xmlns.com/foaf/0.1/")  # only for depictions
    skos = Namespace('http://www.w3.org/2004/02/skos/core#')
    osm = Namespace(cl.getThesaurusString('OSM_WIKI_PAGE'))
    osmNode = osm[cl.getThesaurusString('OSM_NODE')] # = rdflib.term.URIRef(u'http://wiki.openstreetmap.org/wiki/Node')
    osmWay = osm[cl.getThesaurusString('OSM_WAY')] # = rdflib.term.URIRef(u'http://wiki.openstreetmap.org/wiki/Way')
    osmArea = osm[cl.getThesaurusString('OSM_AREA')] # = rdflib.term.URIRef(u'http://wiki.openstreetmap.org/wiki/Area')
    osmRelation = osm[cl.getThesaurusString('OSM_RELATION')] # = rdflib.term.URIRef(u'http://wiki.openstreetmap.org/wiki/Relation')
    osmImplies = osm[cl.getThesaurusString('OSM_IMPLIES')]
    osmCombines = osm[cl.getThesaurusString('OSM_COMBINATION')]
    osmLinks = osm[cl.getThesaurusString('OSM_LINKED')]

    def __init__ (self, filePath=None):
        if filePath is not None:
            self.graph = self.load(filePath)

        self.graph.bind('foaf', self.foaf)
        self.graph.bind('skos', self.skos)
        self.graph.bind('osm', self.osm)
        self.graph.bind('osmNode', self.osmNode)
        self.graph.bind('osmWay', self.osmWay)
        self.graph.bind('osmArea', self.osmArea)
        self.graph.bind('osmRelation', self.osmRelation)
        self.graph.bind('osmImplies', self.osmImplies)
        self.graph.bind('osmCombines', self.osmCombines)
        self.graph.bind('osmLinks', self.osmLinks)


    def load(self, filePath):
        guessedFormat = guess_format(filePath)
        return self.graph.parse(filePath, format=guessedFormat)

    def serialize(self, filepath=(utils.dataDir() + 'default.rdf')):
        plugin.register('skos', Serializer, 'skosserializer', 'SKOSSerializer')  # register(name, kind, module_path, class_name)
        self.graph.serialize(destination=filepath, format='skos', encoding=self.encoding)

    def prepareLiteral(self, objStr):
        objStr = utils.eszettToSS(objStr)
        return objStr

    def addConceptScheme(self, subject):
        self.graph.add((URIRef(subject), RDF.type, SKOS.ConceptScheme))
        return subject

    def addHasTopConcept(self, subject, obj):
        self.graph.add((URIRef(subject), SKOS.hasTopConcept, URIRef(obj)))
        return subject

    def addInScheme(self, subject, obj):
        self.graph.add((URIRef(subject), SKOS.inScheme, URIRef(obj)))
        return subject

    def addConcept(self, subject):
        self.graph.add((URIRef(subject), RDF.type, SKOS.Concept))
        return subject

    def addDefinition(self, subject, obj, language):
        self.graph.add((URIRef(subject), SKOS.definition, Literal(self.prepareLiteral(obj), lang=language)))

    def addScopeNote(self, subject, obj, language):
        self.graph.add((URIRef(subject), SKOS.scopeNote, Literal(self.prepareLiteral(obj), lang=language)))

    def addPrefLabel(self, subject, obj):
        self.graph.add((URIRef(subject), SKOS.prefLabel, Literal(self.prepareLiteral(obj))))
        return subject

    def addAltLabel(self, subject, obj, language):
        self.graph.add((URIRef(subject), SKOS.altLabel, Literal(self.prepareLiteral(obj), lang=language)))
        return subject

    def addNarrower(self, subject, obj):
        '''subject > object. E.g. concept_animals narrower concept_mammals: '''
        self.graph.add((URIRef(subject), SKOS.narrower, URIRef(obj)))
        return subject

    def addBroader(self, subject, obj):
        '''subject > object. E.g. concept_mammals narrower concept_animals: '''
        self.graph.add((URIRef(subject), SKOS.broader, URIRef(obj)))
        return subject

    def addRelated(self, subject, obj):
        self.graph.add((URIRef(subject), SKOS.related, URIRef(obj)))
        return subject

    def addRelatedMatch(self, subject, obj):
        self.graph.add((URIRef(subject), SKOS.relatedMatch, URIRef(obj)))
        return subject

    def addDepiction(self, subject, obj):
        self.graph.add((URIRef(subject), FOAF.depiction, URIRef(obj)))
        return subject

    def addPrefSymbol(self, subject, obj):
        self.graph.add((URIRef(subject), SKOS.prefSymbol, URIRef(obj)))
        return subject

    def addOSMNode(self, subject, obj):
        self.graph.add((URIRef(subject), self.osmNode, Literal(obj)))
        return subject

    def addOSMWay(self, subject, obj):
        self.graph.add((URIRef(subject), self.osmWay, Literal(obj)))
        return subject

    def addOSMArea(self, subject, obj):
        self.graph.add((URIRef(subject), self.osmArea, Literal(obj)))
        return subject

    def addOSMRelation(self, subject, obj):
        self.graph.add((URIRef(subject), self.osmRelation, Literal(obj)))
        return subject

    def addOSMImpliesLiteral(self, subject, obj):
        self.graph.add((URIRef(subject), self.osmImplies, Literal(obj)))
        return subject

    def addOSMImpliesURIRef(self, subject, obj):
        self.graph.add((URIRef(subject), self.osmImplies, URIRef(obj)))
        return subject

    def addOSMCombinesLiteral(self, subject, obj):
        self.graph.add((URIRef(subject), self.osmCombines, Literal(obj)))
        return subject

    def addOSMCombinesURIRef(self, subject, obj):
        self.graph.add((URIRef(subject), self.osmCombines, URIRef(obj)))
        return subject

    def addOSMLinksLiteral(self, subject, obj):
        self.graph.add((URIRef(subject), self.osmLinks, Literal(obj)))
        return subject

    def addOSMLinksURIRef(self, subject, obj):
        self.graph.add((URIRef(subject), self.osmLinks, URIRef(obj)))
        return subject

    def triplesCount(self):
        return len(self.graph)

    def sparqlQuery(self, query):
        return self.graph.query(query)

    def getSubByPrefLabel(self, obj):
        generatorList = self.graph.subjects(SKOS.prefLabel, Literal(obj))
        return utils.genGetFirstItem(generatorList)

    def getInScheme(self, subject):
        generatorList = self.graph.objects(URIRef(subject), SKOS.inScheme)
        return generatorList

    def isInScheme(self, subject, obj):
        refScheme = URIRef(obj)
        generator = self.getInScheme(subject)
        for item in generator:
            if item == refScheme:
                return True
        return False

    def getDefinition(self, subject):
        generatorList = self.graph.objects(URIRef(subject), SKOS.definition)
        return generatorList

    def getScopeNote(self, subject):
        generatorList = self.graph.objects(URIRef(subject), SKOS.scopeNote)
        return generatorList

    def getScopeNoteByLang(self, subject):
        pass

    def getPrefLabels(self, subject):
        generatorList = self.graph.objects(URIRef(subject), SKOS.prefLabel)
        return generatorList

    def getAltLabels(self, subject):
        generatorList = self.graph.objects(URIRef(subject), SKOS.altLabel)
        return generatorList

    def getHiddenLabels(self, subject):
        generatorList = self.graph.objects(URIRef(subject), SKOS.hiddenLabel)
        return generatorList

    def getNarrower(self, subject):
        generatorList = self.graph.objects(URIRef(subject), SKOS.narrower)
        return generatorList

    def getBroader(self, subject):
        generatorList = self.graph.objects(URIRef(subject), SKOS.broader)
        return generatorList

    def getDepiction(self, subject):
        generatorList = self.graph.objects(URIRef(subject), FOAF.depiction)
        return generatorList

    def getPrefSymbol(self, subject):
        generatorList = self.graph.objects(URIRef(subject), SKOS.prefSymbol)
        return generatorList

    def getRelated(self, subject):
        generatorList = self.graph.objects(URIRef(subject), SKOS.related)
        return generatorList

    def getRelatedMatch(self, subject):
        generatorList = self.graph.objects(URIRef(subject), SKOS.relatedMatch)
        return generatorList

    def getOSMNode(self, subject):
        generatorList = self.graph.objects(URIRef(subject), self.osmNode)
        return generatorList

    def getOSMWay(self, subject):
        generatorList = self.graph.objects(URIRef(subject), self.osmWay)
        return generatorList

    def getOSMArea(self, subject):
        generatorList = self.graph.objects(URIRef(subject), self.osmArea)
        return generatorList

    def getOSMRelation(self, subject):
        generatorList = self.graph.objects(URIRef(subject), self.osmRelation)
        return generatorList

    def getSubObjOSMImplies(self):
        genTupleList = self.graph.subject_objects(self.osmImplies)
        return genTupleList

    def getSubObjOSMCombines(self):
        genTupleList = self.graph.subject_objects(self.osmCombines)
        return genTupleList

    def getSubObjOSMLinks(self):
        genTupleList = self.graph.subject_objects(self.osmLinks)
        return genTupleList

    def getOSMImplies(self, subject):
        generatorList = self.graph.objects(URIRef(subject), self.osmImplies)
        return generatorList

    def getOSMCombines(self, subject):
        generatorList = self.graph.objects(URIRef(subject), self.osmCombines)
        return generatorList

    def getOSMLinks(self, subject):
        generatorList = self.graph.objects(URIRef(subject), self.osmLinks)
        return generatorList

    def removeOSMImpliesLiteral(self, subject, obj):
        self.graph.remove( (URIRef(subject), self.osmImplies, Literal(obj)) )

    def removeOSMCombinesLiteral(self, subject, obj):
        self.graph.remove( (URIRef(subject), self.osmCombines, Literal(obj)) )

    def removeOSMLinksLiteral(self, subject, obj):
        self.graph.remove( (URIRef(subject), self.osmLinks, Literal(obj)) )

if __name__ == '__main__':
    r = RDFGraph()

    keyScheme = r.addConceptScheme('www.example.com')

    animals = r.addConcept('www.example.com/animals')
    prefLabel = r.addPrefLabel(animals, 'Animals')
    scopeNote = r.addScopeNote(animals, 'Tiere sind nach biologischem Verständnis eukaryotische Lebewesen, '
                    + 'die ihre Energie nicht durch Photosynthese gewinnen und Sauerstoff '
                    + 'zur Atmung benötigen, aber keine Pilze sind.', 'de')
    altLabel = r.addAltLabel(animals, 'Tier', 'de')
    r.addAltLabel(animals, 'Viech', 'de')
    r.addDepiction(animals, 'http://en.wikipedia.org/wiki/File:Animal_diversity.png')
    r.addInScheme(animals, keyScheme)

    mammals = r.addConcept('www.example.com/mammals')
    r.addPrefLabel(mammals, 'Mammals')
    r.addAltLabel(mammals, 'Säugetier', 'de')
    r.addScopeNote(mammals, 'Die Säugetiere (Mammalia) sind eine Klasse der Wirbeltiere. '
                    'Zu ihren kennzeichnenden Merkmalen gehören das Säugen des Nachwuchses mit Milch', 'de')
    r.addOSMNode(mammals, '50')
    r.addInScheme(mammals, keyScheme)

    r.addOSMImpliesLiteral(animals, 'blubb')
    r.addOSMImpliesURIRef(mammals, 'bliib')

    r.addNarrower(animals, mammals)
    r.addBroader(mammals, animals)
    r.addHasTopConcept(keyScheme, animals)

    r.addRelatedMatch(animals, mammals)

    plugin.register('skos', Serializer, 'skosserializer', 'SKOSSerializer')
    print r.graph.serialize(format='skos', encoding=r.encoding)


    for i, j in r.graph.subject_objects(r.osmImplies):
        print i
        print j
    print '\n'
    r.removeOSMImpliesLiteral(animals, 'blubb')
    print '\n'
    for i, j in r.graph.subject_objects(r.osmImplies):
        print i
        print j
    print '\n'

    graph = Graph()
    g = graph.parse(utils.dataDir() + 'gemet\gemet_concept_en.rdf')
    for i in g.objects(URIRef('http://www.eionet.europa.eu/gemet/concept/8073'), SKOS.prefLabel):
        print i
    print str(len(graph))
