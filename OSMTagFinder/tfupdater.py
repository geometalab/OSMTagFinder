# -*- coding: utf-8 -*-
'''
Created on 06.12.2014

@author: Simon Gwerder
'''

import timeit
import sys

from utilities import utils
from utilities.configloader import ConfigLoader
from thesaurus.updatethesaurus import UpdateThesaurus
from thesaurus.console import Console
from thesaurus.rdfgraph import RDFGraph

if __name__ == '__main__':
    startTime = timeit.default_timer()
    retry = True
    console = Console(sys.stdout)
    cl = ConfigLoader()
    outputName = cl.getThesaurusString('OUTPUT_NAME')
    outputEnding = cl.getThesaurusString('DEFAULT_FORMAT')
    rdfGraph = RDFGraph(utils.outputFile(utils.dataDir(), outputName, outputEnding, useDateEnding=False))
    UpdateThesaurus(rdfGraph, console)

    endTime = timeit.default_timer()
    elapsed = endTime - startTime
    console.println('\nTime elapsed to update rdfGraph: ' + str(elapsed / 60) + ' mins')