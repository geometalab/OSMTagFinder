# -*- coding: utf-8 -*-
'''
Created on 26.09.2014

@author: Simon Gwerder
'''

import os
from rdflib import Graph, Literal, Namespace, RDF, URIRef, plugin
from rdflib.namespace import SKOS
from rdflib.namespace import FOAF
from rdflib.serializer import Serializer
# from skosserializer import SKOSSerializer

class SkosGraph:
    root_dir = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]
    encoding = 'utf-8'
    graph = Graph()
    foaf = Namespace("http://xmlns.com/foaf/0.1/")  # only for depictions
    skos = Namespace('http://www.w3.org/2004/02/skos/core#')
    graph.bind('foaf', foaf)
    graph.bind('skos', skos)


    def serialize(self, filepath):
        plugin.register('skos', Serializer, 'skosserializer', 'SKOSSerializer')  # register(name, kind, module_path, class_name)
        self.graph.serialize(destination=filepath, format='skos', encoding=self.encoding)
        return self.graph.serialize(format='skos', encoding=self.encoding)

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

    def addPrefLabel(self, subject, obj, language):
        self.graph.add((URIRef(subject), SKOS.prefLabel, Literal(obj, lang=language)))
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

if __name__ == '__main__':
    s = SkosGraph()

    scheme = s.addConceptScheme('www.example.com')

    animals = s.addConcept('www.example.com/animals')
    s.addPrefLabel(animals, 'Animals', 'en')
    s.addDefinition(animals, 'Tiere sind nach biologischem Verstaendnis eukaryotische Lebewesen, '
                    + 'die ihre Energie nicht durch Photosynthese gewinnen und Sauerstoff '
                    + 'zur Atmung benoetigen, aber keine Pilze sind.', 'de')
    s.addAltLabel(animals, 'Tier', 'de')
    s.addDepiction(animals, 'http://en.wikipedia.org/wiki/File:Animal_diversity.png')
    s.addInScheme(animals, scheme)

    mammals = s.addConcept('www.example.com/mammals')
    s.addPrefLabel(mammals, 'Mammals', 'en')
    s.addAltLabel(mammals, 'Säugetier', 'de')
    s.addScopeNote(mammals, 'Die Säugetiere (Mammalia) sind eine Klasse der Wirbeltiere.'
    + 'Zu ihren kennzeichnenden Merkmalen gehoeren das Saeugen des Nachwuchses mit Milch, '
    + 'die in den Milchdruesen der Weibchen produziert wird', 'de')
    s.addInScheme(mammals, scheme)

    s.addNarrower(animals, mammals)
    s.addBroader(mammals, animals)
    s.addHasTopConcept(scheme, animals)

    print s.serialize(s.root_dir + '/data/test.rdf')
