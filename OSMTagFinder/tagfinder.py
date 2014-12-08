# -*- coding: utf-8 -*-
'''
Created on 13.11.2014

@author: Simon Gwerder
'''
import os
import time
import datetime
#import sys

#import codecs
#import logging
from utilities import crython

from utilities import utils
from utilities.configloader import ConfigLoader
from website.views import app, loadRdfGraph
from website.indexer import Indexer
from thesaurus.rdfgraph import RDFGraph
from thesaurus.updater import UpdateThesaurus

def runFlaskApp():
    cl = ConfigLoader()
    tagFinderHost = cl.getWebsiteString('HOST')
    tagFinderPort = int(os.environ.get("PORT", cl.getWebsiteInt('PORT')))
    loadRdfGraph()
    app.run(debug=True, host=tagFinderHost, port=tagFinderPort, threaded=True) # TODO debug=False, # Alternately app.run(..., processes=3)


if __name__ == '__main__':

    cl = ConfigLoader()
    @crython.job(expr=cl.getWebsiteString('UPDATE_CRONTAB'))
    def updateJob():
        print 'updating job started'
        cl = ConfigLoader()
        outputName = cl.getThesaurusString('OUTPUT_NAME')
        outputEnding = cl.getThesaurusString('DEFAULT_FORMAT')
        rdfGraph = RDFGraph(utils.outputFile(utils.dataDir(), outputName, outputEnding, useDateEnding=False))
        UpdateThesaurus(rdfGraph) # will update the rdfGraph
        Indexer(rdfGraph) # will index it anew
        today = datetime.date.today().strftime("%d.%m.%y")
        cl.setWebsiteString('DATA_DATE', str(today))
        cl.write() # storing the date change in config file
        runFlaskApp()

    #sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
    #logging.basicConfig()

    cl = ConfigLoader()
    startSched = cl.getWebsiteBoolean('START_SCHEDULER')
    if startSched:
        crython.tab.start()

    runFlaskApp()

    while True:
        time.sleep(86400) # just need this thread to be alive


