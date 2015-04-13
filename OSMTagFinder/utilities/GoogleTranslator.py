# -*- coding: utf-8 -*-
'''
Created on 10.10.2014

@author: Simon Gwerder
'''
import goslate
from utilities.retry import retry

class GoogleTranslator:

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
    
    def translate(self, text, lang=None):
        translated = None
        try:
            if lang == 'de':
                translated = self.translateDEtoEN(text)
            elif lang == 'en':
                translated = self.translateENtoDE(text)
            elif lang is None or not (lang == 'en' or lang == 'de'):
                translated = self.translateToEN(text) # guessing language, is slower
        except:
            pass
        return translated
        



