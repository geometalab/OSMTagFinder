# -*- coding: utf-8 -*-
'''
Created on 26.09.2014

@author: Simon Gwerder
'''

from rdflib import Graph, Literal, Namespace, RDF, URIRef, plugin
from rdflib.namespace import SKOS
from rdflib.namespace import FOAF
from rdflib.serializer import Serializer
from rdflib.util import guess_format
import utils

# from skosserializer import SKOSSerializer

class RDFGraph:
    encoding = 'utf-8'
    graph = Graph()

    def __init__ (self, filePath=None):
        if filePath is not None:
            self.graph = self.load(filePath)
        foaf = Namespace("http://xmlns.com/foaf/0.1/")  # only for depictions
        skos = Namespace('http://www.w3.org/2004/02/skos/core#')
        self.graph.bind('foaf', foaf)
        self.graph.bind('skos', skos)

    def load(self, filePath):
        guessedFormat = guess_format(filePath)
        return self.graph.parse(filePath, format=guessedFormat)

    def serialize(self, filepath=(utils.dataDir() + 'default.rdf')):
        plugin.register('skos', Serializer, 'skosserializer', 'SKOSSerializer')  # register(name, kind, module_path, class_name)
        self.graph.serialize(destination=filepath, format='skos', encoding=self.encoding)

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
        self.graph.add((URIRef(subject), SKOS.definition, Literal(obj, lang=language)))

    def addScopeNote(self, subject, obj, language):
        self.graph.add((URIRef(subject), SKOS.scopeNote, Literal(obj, lang=language)))

    def addPrefLabel(self, subject, obj):
        self.graph.add((URIRef(subject), SKOS.prefLabel, Literal(obj)))
        return subject

    def addAltLabel(self, subject, obj, language):
        self.graph.add((URIRef(subject), SKOS.altLabel, Literal(obj, lang=language)))
        return subject

    def addNarrower(self, subject, obj):
        self.graph.add((URIRef(subject), SKOS.narrower, URIRef(obj)))
        return subject

    def addBroader(self, subject, obj):  # in concept_animals is: ... narrow concept_mammals
        self.graph.add((URIRef(subject), SKOS.broader, URIRef(obj)))
        return subject

    def addDepiction(self, subject, obj):
        self.graph.add((URIRef(subject), FOAF.depiction, URIRef(obj)))
        return subject

    def addPrefSymbol(self, subject, obj):
        self.graph.add((URIRef(subject), SKOS.prefSymbol, URIRef(obj)))
        return subject

    def tripplesCount(self):
        return len(self.graph)

if __name__ == '__main__':
    r = RDFGraph()

    keyScheme = r.addConceptScheme('www.example.com')

    animals = r.addConcept('www.example.com/animals')
    r.addPrefLabel(animals, 'Animals')
    r.addDefinition(animals, 'Tiere sind nach biologischem Verstaendnis eukaryotische Lebewesen, '
                    + 'die ihre Energie nicht durch Photosynthese gewinnen und Sauerstoff '
                    + 'zur Atmung benötigen, aber keine Pilze sind.', 'de')
    r.addAltLabel(animals, 'Tier', 'de')
    r.addDepiction(animals, 'http://en.wikipedia.org/wiki/File:Animal_diversity.png')
    r.addInScheme(animals, keyScheme)

    mammals = r.addConcept('www.example.com/mammals')
    r.addPrefLabel(mammals, 'Mammals')
    r.addAltLabel(mammals, 'Säugetier', 'de')
    r.addScopeNote(mammals, 'Die Säugetiere (Mammalia) sind eine Klasse der Wirbeltiere. '
    + 'Zu ihren kennzeichnenden Merkmalen gehören das Säugen des Nachwuchses mit Milch', 'de')
    r.addInScheme(mammals, keyScheme)

    r.addNarrower(animals, mammals)
    r.addBroader(mammals, animals)
    r.addHasTopConcept(keyScheme, animals)

    plugin.register('skos', Serializer, 'skosserializer', 'SKOSSerializer')
    print r.graph.serialize(format='skos', encoding=r.encoding)


