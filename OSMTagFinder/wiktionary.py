# -*- coding: utf-8 -*-
'''
Created on 26.10.2014

@author: Simon Gwerder
'''

from wikitools import wiki
from wikitools import api

# create a Wiki object
site = wiki.Wiki('http://en.wiktionary.org/w/api.php')
# login - required for read-restricted wikis
# site.login("username", "password")
# define the params for the query
params = {'action': 'opensearch', 'search': 'highway'}
#params = {'action':'query', 'titles':'dog'}
# create the request object
request = api.APIRequest(site, params)
# query the API
result = request.query()
print result