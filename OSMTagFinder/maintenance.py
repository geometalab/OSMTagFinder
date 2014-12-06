# -*- coding: utf-8 -*-
'''
Created on 06.12.2014

@author: Simon Gwerder
'''

from thesaurus.console import Console

from colorama import init, deinit
import sys

if __name__ == '__main__':

    init() #essential for colorama to work on windows

    console = Console(sys.stdout, percentNewLine=False)

    console.printASCIITitle()

    console.printWelcomeMessage() # welcome message
    console.info()
    console.conn()

    console.printNewOrLoad()

    optToActionMap = { '1' : console.create, '2' : console.load }
    console.repeatedOptRead(optToActionMap)

    deinit()