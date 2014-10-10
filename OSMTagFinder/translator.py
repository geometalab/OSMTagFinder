# -*- coding: utf-8 -*-
'''
Created on 10.10.2014

@author: Simon Gwerder
'''
import goslate

class Translator:

    gs = goslate.Goslate()

    def translateENtoDE(self, text):
        return self.gs.translate(text, 'de', 'en')

    def translateDEtoEN(self, text):
        return self.gs.translate(text, 'en', 'de')