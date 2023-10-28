# -*- coding: utf-8 -*-
'''
Created on 10.10.2014

@author: Simon Gwerder
'''
from google_translate import GoogleTranslator
from utilities.retry import retry


class Translator:

    gs = GoogleTranslator()

    @retry(Exception, tries=3)
    def translateENtoDE(self, text):
        return self.gs.translate(text, src_lang='en', dst_lang='de')


    @retry(Exception, tries=3)
    def translateDEtoEN(self, text):
        return self.gs.translate(text, src_lang='de', dst_lang='en')

    @retry(Exception, tries=3)
    def translateToEN(self, text):
        return self.gs.translate(text, src_lang='auto', dst_lang='en')

    @retry(Exception, tries=3)
    def translateToDE(self, text):
        return self.gs.translate(text, src_lang='auto', dst_lang='de')
    
    def translate(self, text, lang=None):
        translated = None
        try:
            if lang == 'de':
                translated = self.translateDEtoEN(text)
            elif lang == 'en':
                translated = self.translateENtoDE(text)
            elif lang is None or not (lang == 'en' or lang == 'de'):
                translated = self.translateToEN(text)  # guessing language, is slower
        except:
            pass
        return translated
        
if __name__ == '__main__':
    t = Translator()
    print(str(t.translate('Uhr', 'de')))
    print(str(t.translate('clock', 'en')))
    print(str(t.translate('This is a pen.', 'en')))
    print(str(t.translate('Das ist ein Stift.', 'de')))


