# -*- coding: utf-8 -*-
'''
Created on 17.10.2014

@author: Simon Gwerder
'''

import datetime
import json
import logging

from flask import Flask, session, send_from_directory, render_template, request, redirect, jsonify, Response
from flask_bootstrap import Bootstrap
from search.graphsearch import GraphSearch
from utilities import utils
from utilities.spellcorrect import SpellCorrect
from web.jsonpdeco import support_jsonp

try:
    # The typical way to import flask-cors. From documentation!
    from flask_cors import cross_origin
except ImportError:
    # This allows examples to be run without installation.
    import os
    parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.sys.path.insert(0, parentdir)
    from flask_cors import cross_origin

websiteRdfGraph = None # global var is assigned in setRdfGraph()! Because there's no way to restart a running 'app' in FLASK!!!
websiteDataDate = datetime.date.today().strftime("%d.%m.%y") # will be assigned aswell
logger = logging.getLogger('VISITOR_LOGGER')
uniqueIP = {} # gathering all IP's that requested during this app's runtime

def setRdfGraph(rdfGraph, dataDate):
    global websiteRdfGraph # blowing your mind, thanks FLASK for beeing so global :(
    websiteRdfGraph = rdfGraph
    global websiteDataDate
    websiteDataDate = dataDate

def createApp():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '#T0P#SECRET#'
    Bootstrap(app)
    #setRdfGraph()
    return app

app = createApp()

def getLocale():
    if 'language' in session:
        return session['language']
    lang = request.accept_languages.best_match(['en', 'de'])
    if lang is None or lang == '':
        lang = 'en'
    setLocale(lang)
    return lang

def setLocale(lang=None):
    if lang is None or lang == '':
        session['language'] = 'en'
    else:
        session['language'] = lang

def addLiteralToLangDict(retDict, literalList):
    for literal in literalList:
        if not hasattr(literal, 'language'): continue # is not Literal in that case
        if literal.language == 'en' or literal.language == 'de':
            listTerms = retDict[str(literal.language)]
            listTerms.append(utils.encode(literal))
            retDict[str(literal.language)] = utils.uniquifyList(listTerms)
    return retDict

def putToUniqueIP(ipAddress):
    if ipAddress in uniqueIP:
        countRequests = uniqueIP[ipAddress]
        countRequests += 1
        uniqueIP[ipAddress] = countRequests
    else:
        uniqueIP[ipAddress] = 1

def searchCall(query, lang=None):
    graphSearch = GraphSearch()
    if websiteRdfGraph is None or query is None or len(query) == 0:
        return None

    if lang is None:
        lang = getLocale()
    return graphSearch.fullSearch(websiteRdfGraph, query, lang)


@app.route('/favicon.ico', methods = ['GET'])
def favicon():
    return send_from_directory(utils.staticDir(), 'ico/favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/tagfinder_thesaurus.rdf', methods = ['GET'])
def tagfindergraph():
    putToUniqueIP(request.remote_addr)
    return send_from_directory(utils.dataDir(), 'tagfinder_thesaurus.rdf', mimetype='application/rdf+xml')

@app.route('/opensearch.xml', methods = ['GET'])
def opensearch():
    putToUniqueIP(request.remote_addr)
    return send_from_directory(utils.templatesDir(), 'opensearch.xml', mimetype='application/opensearchdescription+xml')


@app.route('/', methods = ['GET'])
@app.route('/index', methods = ['GET'])
def index():
    return render_template('search.html', lang=getLocale(), dataDate=websiteDataDate)

@app.route('/setlang', methods = ['POST'])
def setLanguage():
    setLocale(request.form["lang"])
    return '200'

@app.route('/getlang', methods = ['GET'])
def getLanguage():
    return Response(json.dumps(getLocale()), mimetype='application/json')

@app.errorhandler(405)
def methodNotAllowed(e):
    return render_template('405.html', lang=getLocale()), 405

@app.errorhandler(404)
def pageNotFound(e):
    return render_template('404.html', lang=getLocale()), 404


def getThumbnailLink(imageLink):
    if imageLink is None: return imageLink
    imageLink = imageLink.replace('/images/', '/images/thumb/')
    imageLink = imageLink.replace('http://upload.wikimedia.org/wikipedia/commons/', 'http://wiki.openstreetmap.org/w/images/thumb/')
    imageFileName = imageLink[imageLink.rfind('/') + 1:]
    imageLink = imageLink + '/200px-' + imageFileName
    return imageLink

@app.route('/search', methods = ['GET'])
def search():
    query = request.args.get('query', '')
    lang = request.args.get('lang', '')
    searchResults = searchCall(query, lang)
    if searchResults is None:
        return redirect('/')
    for tagResult in searchResults:
        tagResult['thumbnail'] = getThumbnailLink(tagResult['depiction']) # adding a thumbnail version of the 'depiction'
    putToUniqueIP(request.remote_addr)
    logger.info('IP: ' + request.remote_addr + ", search: " + query + ", lang: " + lang)
    return render_template('search.html', lang=getLocale(), query=query, results=searchResults)

@app.route('/apidoc', methods = ['GET'])
def api():
    return render_template('apidoc.html', lang=getLocale())

@app.route('/about', methods = ['GET'])
def about():
    return render_template('about.html', lang=getLocale(), dataDate=websiteDataDate)

@app.route('/api/search', methods = ['GET'])
@cross_origin()
@support_jsonp
def apiSearch():
    query = request.args.get('query', '')
    lang = request.args.get('lang','')
    prettyPrint = request.args.get('format', '')

    if lang is None:
        lang = 'en'

    searchResults = searchCall(query, lang)
    if searchResults is None:
        return jsonify([])

    jsonDump = None

    if prettyPrint is not None and prettyPrint.lower() == 'json_pretty':
        #return jsonify(results=searchResults)
        jsonDump = json.dumps(searchResults, indent=3, sort_keys=True)
    else:
        jsonDump = json.dumps(searchResults)
    putToUniqueIP(request.remote_addr)
    logger.info('IP: ' + request.remote_addr + ", API search: " + query + ", lang: " + lang)
    return Response(jsonDump,  mimetype='application/json')

@app.route('/suggest', methods = ['GET'])
def suggest():
    spellCorrect = SpellCorrect()
    query = request.args.get('query','')

    suggestList = []
    lang = getLocale()

    if lang == 'en':
        suggestList = spellCorrect.listSuggestionsEN(query)
    elif lang == 'de':
        suggestList = spellCorrect.listSuggestionsDE(query)

    #if len(suggestList) == 0:
    #    suggestList = spellCorrect.listSuggestions(word)
    return Response(json.dumps(suggestList), mimetype='application/json')

@app.route('/api/suggest', methods = ['GET'])
@cross_origin()
@support_jsonp
def apiSuggest():
    spellCorrect = SpellCorrect()
    query = request.args.get('query','')
    lang = request.args.get('lang','')
    prettyPrint = request.args.get('format', '')
    suggestList = []
    if lang == 'en':
        suggestList = spellCorrect.listSuggestionsEN(query)
    elif lang == 'de':
        suggestList = spellCorrect.listSuggestionsDE(query)
    else:
        suggestList = spellCorrect.listSuggestions(query)
    if prettyPrint is not None and prettyPrint.lower() == 'json_pretty':
        jsonDump = json.dumps(suggestList, indent=3, sort_keys=True)
    else:
        jsonDump = json.dumps(suggestList)
    putToUniqueIP(request.remote_addr)
    logger.info('IP: ' + request.remote_addr + ", API suggest: " + query + ", lang: " + lang)
    return Response(jsonDump,  mimetype='application/json')

@app.route('/ossuggest', methods = ['GET'])
@cross_origin()
@support_jsonp
def osSuggest():
    spellCorrect = SpellCorrect()
    query = request.args.get('query','')
    suggestList = []
    lang = getLocale()
    if lang == 'en':
        suggestList = spellCorrect.listSuggestionsEN(query)
    elif lang == 'de':
        suggestList = spellCorrect.listSuggestionsDE(query)
    opensearchSug = [query, suggestList, [], []]
    jsonDump = json.dumps(opensearchSug)
    return Response(jsonDump,  mimetype='application/json')


@app.route('/api/tag', methods = ['GET'])
@cross_origin()
@support_jsonp
def apiTag():
    prefLabel = None
    key = request.args.get('key','')
    if websiteRdfGraph is None or key is None or len(key) == 0:
        return jsonify({})
    value = request.args.get('value')
    if not value == '*' and not value is None and not len(value) == 0 :
        prefLabel = key + '=' + value
    else:
        prefLabel = key
    subject = websiteRdfGraph.getSubByPrefLabel(prefLabel)
    # subject will only be tag subject and not term subject, because of missing language
    if subject is None:
        return jsonify({})

    rawResults = { subject : { } } # add empty dictionary for the searchMeta
    graphSearch = GraphSearch()
    results = graphSearch.getSortedTagResults(websiteRdfGraph, rawResults)
    if len(results) < 1:
        return jsonify({})

    prettyPrint = request.args.get('format', '')
    if prettyPrint is not None and prettyPrint.lower() == 'json_pretty':
        jsonDump = json.dumps(results[0], indent=3, sort_keys=True)
    else:
        jsonDump = json.dumps(results[0])
    putToUniqueIP(request.remote_addr)
    logger.info('IP: ' + request.remote_addr + ", API tag: " + prefLabel)
    return Response(jsonDump,  mimetype='application/json')

@app.route('/api/terms', methods = ['GET'])
@cross_origin()
@support_jsonp
def apiTerms():
    term = request.args.get('term','')
    prettyPrint = request.args.get('format', '')

    listRelatedMatches = []

    if websiteRdfGraph is None or term is None or len(term) == 0:
        return jsonify({})

    # subject will only be term subject and not tag subject, because of language
    listRelatedMatches.extend( websiteRdfGraph.getSubByPrefLabelLang(term, 'en') )
    listRelatedMatches.extend( websiteRdfGraph.getSubByPrefLabelLang(term, 'de') )
    listRelatedMatches.extend( websiteRdfGraph.getSubByAltLabelLang(term, 'en') )
    listRelatedMatches.extend( websiteRdfGraph.getSubByAltLabelLang(term, 'de') )
    listRelatedMatches.extend( websiteRdfGraph.getSubByBroaderLang(term, 'en') )
    listRelatedMatches.extend( websiteRdfGraph.getSubByBroaderLang(term, 'de') )
    listRelatedMatches.extend( websiteRdfGraph.getSubByNarrowerLang(term, 'en') )
    listRelatedMatches.extend( websiteRdfGraph.getSubByNarrowerLang(term, 'de') )

    termRelated  = { 'en' : [], 'de' : [] }
    termBroader  = { 'en' : [], 'de' : [] }
    termNarrower = { 'en' : [], 'de' : [] }

    for relSubject in listRelatedMatches:
        termRelated = addLiteralToLangDict(termRelated, utils.genToList(websiteRdfGraph.getPrefLabel(relSubject)))
        termRelated = addLiteralToLangDict(termRelated, utils.genToList(websiteRdfGraph.getAltLabel(relSubject)))
        termBroader = addLiteralToLangDict(termBroader, utils.genToList(websiteRdfGraph.getBroader(relSubject)))
        termNarrower = addLiteralToLangDict(termNarrower, utils.genToList(websiteRdfGraph.getNarrower(relSubject)))

    retDict = {}
    retDict['termRelated'] = termRelated
    retDict['termBroader'] = termBroader
    retDict['termNarrower'] = termNarrower

    if prettyPrint is not None and prettyPrint.lower() == 'json_pretty':
        jsonDump = json.dumps(retDict, indent=3, sort_keys=True)
    else:
        jsonDump = json.dumps(retDict)
    putToUniqueIP(request.remote_addr)
    logger.info('IP: ' + request.remote_addr + ", API terms: " + term)
    return Response(jsonDump,  mimetype='application/json')

@app.route('/api/uniqueips', methods = ['GET'])
@cross_origin()
@support_jsonp
def uniqueIPs():
    prettyPrint = request.args.get('format', '')
    if prettyPrint is not None and prettyPrint.lower() == 'json_pretty':
        jsonDump = json.dumps(uniqueIP, indent=3, sort_keys=True)
    else:
        jsonDump = json.dumps(uniqueIP)
    return Response(jsonDump,  mimetype='application/json')





