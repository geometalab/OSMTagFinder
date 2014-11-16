# -*- coding: utf-8 -*-
'''
Created on 10.10.2014

@author: Simon Gwerder
'''
import goslate
from utilities.retry import retry

class Translator:

    gs = goslate.Goslate()

    @retry(Exception, tries=3)
    def translateENtoDE(self, text):
        return self.gs.translate(text, 'de', 'en')

    @retry(Exception, tries=3)
    def translateDEtoEN(self, text):
        return self.gs.translate(text, 'en', 'de')

    @retry(Exception, tries=3)
    def translateToEN(self, text):
        lang = self.gs.detect(text)
        if lang is None or lang == '':
            lang = 'de'
        return self.gs.translate(text, 'en', lang)

    @retry(Exception, tries=3)
    def translateToDE(self, text):
        lang = self.gs.detect(text)
        if lang is None or lang == '':
            lang = 'en'
        return self.gs.translate(text, 'de', lang)
