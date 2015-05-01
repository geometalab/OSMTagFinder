# -*- coding: utf-8 -*-
'''
Created on 13.11.2014

@author: Simon Gwerder
Thanks go to Tom (bashzestampeedo) aswell, who helped me when learning python got to me - nice Canadian guy!!
'''
import os
import time
import datetime
import logging
import sys
#import codecs

from utilities import crython

from utilities import utils
from utilities.configloader import ConfigLoader
from web.views import app, setRdfGraph
from thesaurus.rdfgraph import RDFGraph
from thesaurus.updatethesaurus import UpdateThesaurus
from taginfo.taginfo import TagInfo

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

def runFlaskApp(rdfGraph=None, dataDate=None):
    logging.info('Application started')
    print 'Server Running'
    cl = ConfigLoader()

    if rdfGraph is None or dataDate is None:
        outputName = cl.getThesaurusString('OUTPUT_NAME')
        outputEnding = cl.getThesaurusString('DEFAULT_FORMAT')
        rdfGraph = RDFGraph(utils.outputFile(utils.dataDir(), outputName, outputEnding, useDateEnding=False))
        dataDate = cl.getWebsiteString('DATA_DATE')

    setRdfGraph(rdfGraph, dataDate)

    #tagFinderHost = cl.getWebsiteString('HOST')
    tagFinderPort = int(os.environ.get("PORT", cl.getWebsiteInt('PORT')))
    
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(port=tagFinderPort)
    IOLoop.instance().start()
    
    #app.run(debug=False, host=tagFinderHost, port=tagFinderPort, threaded=True) # debug=False/True, alternately app.run(..., processes=3)

def initLogger():
    tornadoAccessLog = logging.getLogger("tornado.access")
    tornadeAppLog = logging.getLogger("tornado.application")
    tornadoGeneralLog = logging.getLogger("tornado.general")
    
    logFile = utils.outputFile(utils.logDir(), 'serverlog', '.log', False)
    logging.basicConfig(format='%(asctime)s: %(levelname)s - %(message)s', filemode='w', filename=logFile, level=logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    
    logger = logging.getLogger('VISITOR_LOGGER')
    logger.setLevel(logging.INFO)
    
    visitorFile = utils.outputFile(utils.logDir(), 'visitorlog', '.log', False)
    # create a file handler
    handler = logging.FileHandler(visitorFile)
    handler.setLevel(logging.INFO)
    
    # create a logging format
    formatter = logging.Formatter('%(asctime)s: %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    # add the handlers to the logger
    logger.addHandler(tornadeAppLog)
    logger.addHandler(tornadoAccessLog)
    logger.addHandler(tornadoGeneralLog)
    logger.addHandler(handler)
    logger.addHandler(ch)
    
    

if __name__ == '__main__':

    initLogger()
    cl = ConfigLoader()
    @crython.job(expr=cl.getWebsiteString('UPDATE_CRONTAB'))
    def updateJob():
        print 'Updating job started'
        initLogger()
        logging.info('Updating job started')
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


    cl = ConfigLoader()
    startSched = cl.getWebsiteBoolean('START_SCHEDULER')
    if startSched:
        crython.tab.start()

    runFlaskApp()

    while True:
        time.sleep(86400) # just need this thread to be alive


