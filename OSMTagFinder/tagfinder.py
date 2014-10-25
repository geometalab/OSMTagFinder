# -*- coding: utf-8 -*-
'''
Created on 17.10.2014

@author: Simon Gwerder
'''
import os
from flask import Flask, session, send_from_directory, render_template, request, redirect
from flask_bootstrap import Bootstrap

from utilities.configloader import ConfigLoader
from utilities import utils
from thesaurus.rdfgraph import RDFGraph
from thesaurus.tagresults import TagResults
from thesaurus.graphsearch import GraphSearch


rdfGraph = RDFGraph(utils.dataDir() + 'osm_tag_thesaurus_141020.rdf')

app = Flask(__name__)
app.config['SECRET_KEY'] = '#T0P#SECRET#'
Bootstrap(app)

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



@app.route('/favicon.ico')
def favicon():
    return send_from_directory(utils.staticDir(), '/ico/favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/', methods = ['GET'])
@app.route('/index', methods = ['GET'])
def index():
    return render_template('search.html', lang=getLocale())

@app.route('/lang', methods = ['POST'])
def changeLanguage():
    setLocale(request.form["lang"])
    return '200'

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', lang=getLocale()), 404

@app.route('/search', methods = ['GET'])
def search():
    graphSearch = GraphSearch()
    q = request.args.get('q', '')
    if q is None or q == '':
        return redirect('/')

    rawResults = graphSearch.extendedSearch(q)
    searchResults = TagResults(rdfGraph, rawResults)

    return render_template('search.html', lang=getLocale(), q=q, results=searchResults.getResults())

if __name__ == '__main__':
    cl = ConfigLoader()
    tagFinderHost = cl.getWebsiteString('HOST')
    tagFinderPort = int(os.environ.get("PORT", cl.getWebsiteInt('PORT')))
    app.run(debug=True, host=tagFinderHost, port=tagFinderPort) # TODO debug=False




