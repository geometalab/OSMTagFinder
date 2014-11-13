# -*- coding: utf-8 -*-
'''
Created on 13.11.2014

@author: Simon Gwerder
'''
import os

from utilities.configloader import ConfigLoader
from website.views import app

if __name__ == '__main__':
    cl = ConfigLoader()
    tagFinderHost = cl.getWebsiteString('HOST')
    tagFinderPort = int(os.environ.get("PORT", cl.getWebsiteInt('PORT')))
    app.run(debug=True, host=tagFinderHost, port=tagFinderPort, threaded=True) # TODO debug=False, # Alternately app.run(..., processes=3)