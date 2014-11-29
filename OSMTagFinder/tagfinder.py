# -*- coding: utf-8 -*-
'''
Created on 13.11.2014

@author: Simon Gwerder
'''
import os
#import sys
#import codecs

from utilities.configloader import ConfigLoader
from website.views import app
#import logging

if __name__ == '__main__':

    #sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
    #logging.basicConfig()

    cl = ConfigLoader()
    tagFinderHost = cl.getWebsiteString('HOST')
    tagFinderPort = int(os.environ.get("PORT", cl.getWebsiteInt('PORT')))
    app.run(debug=False, host=tagFinderHost, port=tagFinderPort, threaded=True) # TODO debug=False, # Alternately app.run(..., processes=3)