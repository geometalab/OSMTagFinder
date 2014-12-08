# -*- coding: utf-8 -*-
'''
Created on 17.10.2014

@author: Simon Gwerder
'''

import json
from flask import Flask, session, send_from_directory, render_template, request, redirect, jsonify, Response
from flask_bootstrap import Bootstrap
from utilities.jsonpdeco import support_jsonp
import datetime


from utilities import utils
from utilities.configloader import ConfigLoader
from thesaurus.rdfgraph import RDFGraph
from website.tagresults import TagResults
from website.graphsearch import GraphSearch
from utilities.spellcorrect import SpellCorrect

try:
    # The typical way to import flask-cors. From documentation!
    from flask.ext.cors import cross_origin
except ImportError:
    # This allows examples to be run without installation.
    import os
    parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.sys.path.insert(0, parentdir)
    from flask.ext.cors import cross_origin

websiteRdfGraph = None # global var is assigned in loadRdfGraph()! Because there's no way to restart a running 'app' in FLASK!!!
dataDate = datetime.date.today().strftime("%d.%m.%y") # will be assigned aswell

def loadRdfGraph():
    cl = ConfigLoader()
    outputName = cl.getThesaurusString('OUTPUT_NAME')
    outputEnding = cl.getThesaurusString('DEFAULT_FORMAT')
    global websiteRdfGraph # blowing your mind, thanks FLASK for beeing so global :(
    websiteRdfGraph = RDFGraph(utils.outputFile(utils.dataDir(), outputName, outputEnding, useDateEnding=False))
    global dataDate
    dataDate = cl.getWebsiteString('DATA_DATE')

def createApp():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '#T0P#SECRET#'
    Bootstrap(app)
    loadRdfGraph()
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


def searchCall(query, lang=None):
    graphSearch = GraphSearch()
    if websiteRdfGraph is None or query is None or len(query) == 0:
        return None

    if lang is None:
        lang = getLocale()

    rawResults = graphSearch.fullSearch(query, lang)

    return TagResults(websiteRdfGraph, rawResults)

@app.route('/favicon.ico', methods = ['GET'])
def favicon():
    return send_from_directory(utils.staticDir(), 'ico/favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/tagfinder_thesaurus.rdf', methods = ['GET'])
def tagfindergraph():
    return send_from_directory(utils.dataDir(), 'tagfinder_thesaurus.rdf', mimetype='application/rdf+xml')

@app.route('/search/opensearch.xml', methods = ['GET'])
def opensearch():
    return send_from_directory(utils.templatesDir(), 'opensearch.xml', mimetype='application/opensearchdescription+xml')


@app.route('/', methods = ['GET'])
@app.route('/index', methods = ['GET'])
def index():
    return render_template('search.html', lang=getLocale(), dataDate=dataDate)

@app.route('/lang', methods = ['POST'])
def changeLanguage():
    setLocale(request.form["lang"])
    return '200'

@app.errorhandler(405)
def methodNotAllowed(e):
    return render_template('405.html', lang=getLocale()), 405

@app.errorhandler(404)
def pageNotFound(e):
    return render_template('404.html', lang=getLocale()), 404

@app.route('/search', methods = ['GET'])
def search():
    q = request.args.get('q', '')
    searchResults = searchCall(q)
    if searchResults is None:
        return redirect('/')

    return render_template('search.html', lang=getLocale(), q=q, results=searchResults.getResults())

@app.route('/api/search', methods = ['GET'])
@cross_origin()
@support_jsonp
def apiSearch():
    query = request.args.get('q', '')
    lang = request.args.get('lang','')
    prettyPrint = request.args.get('prettyprint', '')

    if lang is None:
        lang = 'en'

    searchResults = searchCall(query, lang)
    if searchResults is None:
        return jsonify([])

    jsonDump = None

    if prettyPrint is not None and prettyPrint.lower() == 'true':
        #return jsonify(results=searchResults.getResults())
        jsonDump = json.dumps(searchResults.getResults(), indent=4, sort_keys=True)
    else:
        jsonDump = json.dumps(searchResults.getResults())
    return Response(jsonDump,  mimetype='application/json')

@app.route('/suggest', methods = ['GET'])
def suggest():
    spellCorrect = SpellCorrect()
    query = request.args.get('q','')

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
    query = request.args.get('q','')
    lang = request.args.get('lang','')
    prettyPrint = request.args.get('prettyprint', '')

    suggestList = []

    if lang == 'en':
        suggestList = spellCorrect.listSuggestionsEN(query)
    elif lang == 'de':
        suggestList = spellCorrect.listSuggestionsDE(query)
    else:
        suggestList = spellCorrect.listSuggestions(query)

    if prettyPrint is not None and prettyPrint.lower() == 'true':
        jsonDump = json.dumps(suggestList, indent=4, sort_keys=True)
    else:
        jsonDump = json.dumps(suggestList)

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
    results = TagResults(websiteRdfGraph, rawResults)
    if len(results.getResults()) < 1:
        return jsonify({})

    prettyPrint = request.args.get('prettyprint', '')
    if prettyPrint is not None and prettyPrint.lower() == 'true':
        jsonDump = json.dumps(results.getResults()[0], indent=4, sort_keys=True)
    else:
        jsonDump = json.dumps(results.getResults()[0])

    return Response(jsonDump,  mimetype='application/json')

@app.route('/api/terms', methods = ['GET'])
@cross_origin()
@support_jsonp
def apiTerms():
    term = request.args.get('term','')
    prettyPrint = request.args.get('prettyprint', '')

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

    if prettyPrint is not None and prettyPrint.lower() == 'true':
        jsonDump = json.dumps(retDict, indent=4, sort_keys=True)
    else:
        jsonDump = json.dumps(retDict)

    return Response(jsonDump,  mimetype='application/json')






