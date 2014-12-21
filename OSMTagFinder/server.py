# -*- coding: utf-8 -*-
'''
Created on 13.11.2014

@author: Simon Gwerder
Thanks go to Tom (bashzestampeedo) aswell, who helped me when learning python got to me - nice Canadian guy!!
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
from web.views import app, setRdfGraph
from thesaurus.rdfgraph import RDFGraph
from thesaurus.updatethesaurus import UpdateThesaurus
from taginfo.taginfo import TagInfo

def runFlaskApp(rdfGraph=None, dataDate=None):
    cl = ConfigLoader()

    if rdfGraph is None or dataDate is None:
        outputName = cl.getThesaurusString('OUTPUT_NAME')
        outputEnding = cl.getThesaurusString('DEFAULT_FORMAT')
        rdfGraph = RDFGraph(utils.outputFile(utils.dataDir(), outputName, outputEnding, useDateEnding=False))
        dataDate = cl.getWebsiteString('DATA_DATE')

    setRdfGraph(rdfGraph, dataDate)

    tagFinderHost = cl.getWebsiteString('HOST')
    tagFinderPort = int(os.environ.get("PORT", cl.getWebsiteInt('PORT')))
    app.run(debug=False, host=tagFinderHost, port=tagFinderPort, threaded=True) # debug=False/True, alternately app.run(..., processes=3)


if __name__ == '__main__':

    cl = ConfigLoader()
    @crython.job(expr=cl.getWebsiteString('UPDATE_CRONTAB'))
    def updateJob():
        print 'updating job started'
        cl = ConfigLoader()
        outputName = cl.getThesaurusString('OUTPUT_NAME')
        outputEnding = cl.getThesaurusString('DEFAULT_FORMAT')
        rdfGraph = RDFGraph(utils.outputFile(utils.dataDir(), outputName, outputEnding, useDateEnding=False))
        tagInfo = TagInfo()
        UpdateThesaurus(tagInfo=tagInfo, rdfGraph=rdfGraph, console=None) # will update the rdfGraph
        today = str(datetime.date.today().strftime("%d.%m.%y"))
        cl.setWebsiteString('DATA_DATE', today)
        cl.write() # storing the date change in config file
        runFlaskApp(rdfGraph, today)

    #sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
    #logging.basicConfig()

    cl = ConfigLoader()
    startSched = cl.getWebsiteBoolean('START_SCHEDULER')
    if startSched:
        crython.tab.start()

    runFlaskApp()

    while True:
        time.sleep(86400) # just need this thread to be alive


