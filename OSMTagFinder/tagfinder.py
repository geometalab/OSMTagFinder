# -*- coding: utf-8 -*-
'''
Created on 17.10.2014

@author: Simon Gwerder
'''
from flask import Flask, send_from_directory, render_template, request, redirect

from utilities.configloader import ConfigLoader
from utilities import utils

app = Flask(__name__)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(utils.staticDir(), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/', methods = ['GET'])
def index():
    author = "Simon"
    name = "You"
    return render_template('index.html', author=author, name=name)

@app.route('/search', methods = ['GET'])
def search():
    term = request.args.get('term', '')
    if term is None or term == '':
        return redirect('/')
    return render_template('index.html', term=term, fieldvalue=term)

if __name__ == '__main__':
    cl = ConfigLoader()
    tagFinderHost = cl.getWebsiteString('HOST')
    tagFinderPort = cl.getWebsiteInt('PORT')
    app.run(host=tagFinderHost, port=tagFinderPort)