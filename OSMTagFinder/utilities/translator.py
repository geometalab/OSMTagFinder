# -*- coding: utf-8 -*-
'''
Created on 10.10.2014

@author: Simon Gwerder
'''
from utilities.MicrosoftTranslator import MicrosoftTranslator
from utilities.retry import retry


class Translator:
    
    translator = MicrosoftTranslator()

    @retry(Exception, tries=3)
    def translateENtoDE(self, text):
        return self.translator.translate(text, 'de', 'en')

    @retry(Exception, tries=3)
    def translateDEtoEN(self, text):
        return self.translator.translate(text, 'en', 'de')

    @retry(Exception, tries=3)
    def translateToEN(self, text):
        return self.translator.translate(text, 'en')

    @retry(Exception, tries=3)
    def translateToDE(self, text):
        return self.translator.translate(text, 'de')
    
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
        



