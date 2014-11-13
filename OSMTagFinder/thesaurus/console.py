# -*- coding: utf-8 -*-
'''
Created on 10.11.2014

@author: Simon Gwerder
'''
import time
import timeit
import sys
from colorama import init, deinit
from termcolor import colored

from utilities import utils
from basethesaurus import BaseThesaurus

class Console:

    fileDescr = None
    percentNewLine = True

    __partInt = 0
    __totalInt = 0
    __commands = { }
    prefix = '>'
    unknownMsg = 'Undefined suggestion or command.'

    rdfGraph = None

    def __init__(self, fileDescriptor=None, percentNewLine=True):
        self.fileDescr = fileDescriptor # e.g sys.stdout
        self.percentNewLine = percentNewLine

        self.__commands['-info'] = self.info # adding function pointer to command
        self.__commands['-load'] = self.load
        self.__commands['-save'] = self.save
        self.__commands['-exit'] = self.exit

    def getPercentDoneStr(self, partInt, totalInt, workingOn=None):

        self.__partInt = partInt
        self.__totalInt = totalInt

        if totalInt == 0: return ' 100% - Done!'

        percent = (int) ((abs(float(partInt)) / abs(float(totalInt))) * 100)

        if workingOn is not None:
            workingOn = ' - Working on: ' + workingOn
        else:
            workingOn = ''

        if percent < 10:
            return '   ' + str(abs(percent)) + '%' + workingOn
        elif abs(percent) < 100:
            return '  ' + str(abs(percent)) + '%' + workingOn
        else:
            self.__partInt = 0
            self.__totalInt = 0
            if workingOn is not None:
                return ' 100%'
            else:
                return ' 100% - Done!'

    def appendEmptyLine(self, s):
        if len(str(s)) > 79:  # windows console
            s = s[:76] + '...'
            return s

        emptyLine = ''
        i = 0
        while i < 79 - len(s):
            emptyLine = emptyLine + ' '
            i = i + 1
        return s + emptyLine

    def restartline(self):
        if self.fileDescr is None: return
        self.fileDescr.write('\r')
        self.fileDescr.flush()

    def printstr(self, s):
        if self.fileDescr is None: return
        self.fileDescr.write(self.appendEmptyLine(s))
        self.fileDescr.flush()
        self.restartline()

    def println(self, s):
        if self.fileDescr is None: return
        self.fileDescr.write(s + '\n')
        self.fileDescr.flush()

    def printlnColored(self, s, foreground=None, background=None):
        '''From termcolor:
        'foreground' strings: grey, red, green, yellow, blue, magenta, cyan, white
        'background' strings: on_grey, on_red, on_green, on_yellow, on_blue, on_magenta, on_cyan, on_white'''
        self.println(colored(s, foreground, background))

    def sleep(self, seconds):
        try:
            time.sleep(seconds) # wait 'seconds' seconds...
        except:
            pass

    def printPercent(self, partInt, totalInt, workingOn=None):
        if self.percentNewLine:
            self.println(self.getPercentDoneStr(partInt, totalInt, workingOn))
        else:
            self.printstr(self.getPercentDoneStr(partInt, totalInt, workingOn))
            if(partInt >= totalInt):
                self.println('')

    def printWorkingOn(self, workingOn):
        self.printPercent(self.__partInt, self.__totalInt, workingOn)

    def printlnWhiteOnBlue(self, s):
        self.printlnColored(self.appendEmptyLine(s), 'white', 'on_blue')

    def printlnGreyOnBlue(self, s):
        self.printlnColored(self.appendEmptyLine(s), 'grey', 'on_blue')

    def printlnWhiteOnCyan(self, s):
        self.printlnColored(self.appendEmptyLine(s), 'white', 'on_cyan')

    def printlnWhiteOnGreen(self, s):
        self.printlnColored(self.appendEmptyLine(s), 'white', 'on_green')

    def printlnGreyOnGreen(self, s):
        self.printlnColored(self.appendEmptyLine(s), 'grey', 'on_green')

    def printASCIITitle(self):
        self.println(' _______          ______ _           _')
        self.println('|__   __|        |  ____(_)         | |')
        self.println('   | | __ _  __ _| |__   _ _ __   __| | ___ _ __')
        self.println('   | |/ _` |/ _` |  __| | | \'_ \ / _` |/ _ \ \'__|')
        self.println('   | | (_| | (_| | |    | | | | | (_| |  __/ |')
        self.println('   |_|\__,_|\__, |_|    |_|_| |_|\__,_|\___|_|')
        self.println('             __/ |')
        self.println('            |___/')
        self.println(' _______ _')
        self.println('|__   __| |')
        self.println('   | |  | |__   ___  ___  __ _ _   _ _ __ _   _ ___')
        self.println('   | |  | \'_ \\ / _ \\/ __|/ _` | | | | \'__| | | / __|')
        self.println('   | |  | | | |  __/\\__ \\ (_| | |_| | |  | |_| \\__ \\')
        self.println('   |_|  |_| |_|\___||___/\__,_|\__,_|_|   \__,_|___/')
        self.println('')

    def printWelcomeMessage(self):
        self.printlnWhiteOnBlue('')
        self.printlnWhiteOnBlue(' TagFinder Thesaurus Maintenance v.1.0')
        self.printlnWhiteOnBlue('')
        self.printlnWhiteOnBlue(' This is a console application to create and maintain a Open Street Map')
        self.printlnWhiteOnBlue(' TagFinder Thesaurus RDF graph')
        self.printlnGreyOnBlue(' Requires Internet connection')
        self.printlnWhiteOnBlue('')

    def info(self):
        self.println('')
        self.printlnWhiteOnBlue('')
        self.printlnWhiteOnBlue(' Commands: ')
        self.printlnWhiteOnBlue(' The following commands can only be used while this application is waiting for')
        self.printlnWhiteOnBlue(' input and not as application arguments. They start with a hyphen')
        self.printlnGreyOnBlue(' (e.g. -info)')
        self.printlnWhiteOnBlue('')
        self.printlnWhiteOnBlue(' -info  : prints this info panel')
        self.printlnWhiteOnBlue(' -load  : loading routine for existing TagFinder graphs')
        self.printlnWhiteOnBlue(' -save  : serializes the current TagFinder graph and your editing-position')
        self.printlnWhiteOnBlue(' -final : serializes the TagFinder graph and performs finalizing operations')
        self.printlnWhiteOnBlue(' -exit  : terminates this application')
        self.printlnWhiteOnBlue('')
        self.printlnWhiteOnBlue('')
        self.printlnWhiteOnBlue(' Suggestion lists:')
        self.printlnWhiteOnBlue(' When choosing items from a suggestion list you can just use the according')
        self.printlnWhiteOnBlue(' number or write down your own terms explicitly. Multiple items can be')
        self.printlnWhiteOnBlue(' separated with a comma. They can not be mixed with commands.')
        self.printlnGreyOnBlue(' (e.g. 3-5, 7, Zoo, Tierpark, 1)')
        self.printlnWhiteOnBlue('')
        self.printlnWhiteOnBlue(' Pressing "Enter" confirms the inputs')
        self.printlnWhiteOnBlue('')
        self.println('')

    def printNewOrLoad(self):
        self.println('')
        self.printlnWhiteOnGreen('')
        self.printlnWhiteOnGreen(' Intializing options:')
        self.printlnWhiteOnGreen('')
        self.println('')
        self.println(' [1] - Create a new TagFinder graph, based on Open Street Map keys and tags.')
        self.println(' [2] - Load an existing TagFinder graph at its last editing position.')
        self.println('')

    def create(self):
        self.println('')
        self.printlnWhiteOnGreen('')
        self.printlnWhiteOnGreen(' Creating a new TagFinder graph (can take up to 25 minutes):')
        self.printlnWhiteOnGreen('')
        self.println('')

        startTime = timeit.default_timer()
        bt = BaseThesaurus(self)
        endTime = timeit.default_timer()
        elapsed = endTime - startTime
        self.println('\n Time elapsed: ' + str((int) (elapsed / 60)) + ' mins')
        self.println(' Number of keys: ' + str(bt.numberKeys))
        self.println(' Number tags: ' + str(bt.numberTags))
        self.println (' Tripples: ' + str(bt.getBaseGraph().triplesCount()))
        self.rdfGraph = bt.getBaseGraph()

    def loadGraph(self, filePath):
        print 'LoadGraph from: ' + filePath

    def load(self):
        self.println('')
        self.printlnWhiteOnGreen('')
        self.printlnWhiteOnGreen(' Loading options:')
        self.printlnWhiteOnGreen('')
        self.println('')

        optionCount = 1
        optToActionMap = { }
        optToParamMap = { }

        for f in utils.fileLoader(utils.dataDir() + 'temp\\', '.rdf'):
            filename = f[f.rfind('\\') + 1 : len(f)] # r(everse )find: lastindexof
            self.println(' [' + str(optionCount) + '] - ' + filename)
            optToActionMap[str(optionCount)] = self.loadGraph
            optToParamMap[str(optionCount)] = f
            optionCount = optionCount + 1
        self.println('')

        self.repeatedOptRead(optToActionMap, optToParamMap) # self.rdfGraph isn't None after this

        self.edit()


    def save(self):
        print('saved') #TODO

    def edit(self):
        print('edited') #TODO

    def exit(self):
        sys.exit()

    def runCommand(self, inputText):
        for commandKey in self.__commands:
            if commandKey == inputText:
                command = self.__commands[commandKey]
                command()  # executes passed function 'action'
                return True
        return False

    def runSuggestions(self, inputText, numToStrMap, action):
        preparedList = self.prepSuggestions(inputText, numToStrMap)
        if len(preparedList) == 0:
            return False # there was some wrong input
        else:
            for item in preparedList:
                action(item)
        return True

    def runOptions(self, inputText, optToActionMap, optToParamMap=None):
        if inputText in optToActionMap:
            action = optToActionMap[inputText]
            if optToParamMap is not None and inputText in optToParamMap:
                param = optToParamMap[inputText]
                action(param) # executes passed function 'action' with params
            else:
                action() # executes passed function 'action'
            return True
        return False

    def readLine(self, prefix='>'):
        inputText = raw_input(prefix)
        return inputText

    def repeatedOptRead(self, optToActionMap, optToParamMap=None, intro=None):
        didAction = False
        while(not didAction):
            if intro is not None: intro()  # executes passed function 'intro'
            inputText = self.readLine(self.prefix)
            inputText = inputText.replace('[', '')
            inputText = inputText.replace(']', '')
            inputText = inputText.strip()
            wasCommand = self.runCommand(inputText)
            if not wasCommand:
                didAction = self.runOptions(inputText, optToActionMap, optToParamMap)
                if not didAction:
                    self.println(self.unknownMsg + '\n')

    def repeatedSugRead(self, numToStrMap, action, intro=None):
        didAction = False
        while(not didAction):
            if intro is not None: intro() # executes passed function 'action'
            inputText = self.readLine(self.prefix)
            inputText = inputText.replace('[', '')
            inputText = inputText.replace(']', '')
            inputText = inputText.strip()
            wasCommand = self.runCommand(inputText)
            if not wasCommand:
                didAction = self.runSuggestions(inputText, numToStrMap, action)
                if not didAction:
                    self.println(self.unknownMsg + '\n')

    def prepSuggestions(self, inputText, numToStrMap):
        retList = []
        inputText = inputText.replace(' , ', ',')
        inputText = inputText.replace(', ', ',')
        splitComma = inputText.split(',')

        for item in splitComma:
            item = item.strip()
            if utils.isNumber(item) and item in numToStrMap:
                retList.append(numToStrMap[item])
            elif utils.isNumber(item) and item not in numToStrMap:
                return [] # wrong input, return empty list
            elif '-' in item:
                splitHyphen = item.split('-')
                firstIsNumber = utils.isNumber(splitHyphen[0].strip())
                secondIsNumber =  utils.isNumber(splitHyphen[1].strip())
                if len(splitHyphen) == 2 and firstIsNumber and secondIsNumber:
                    firstNumber = (int) (splitHyphen[0].strip())
                    secondNumber = (int) (splitHyphen[1].strip())
                    while(firstNumber <= secondNumber):
                        if str(firstNumber) in numToStrMap:
                            retList.append(numToStrMap[str(firstNumber)])
                        else:
                            return [] # wrong input, return empty list
                        firstNumber = firstNumber + 1
                else: retList.append(item)
            else: retList.append(item)
        return retList



if __name__ == '__main__':

    init() #essential for colorama to work on windows

    console = Console(sys.stdout, percentNewLine=False)

    console.printASCIITitle()

    console.printWelcomeMessage() # welcome message
    console.info()

    console.sleep(2)

    console.printNewOrLoad()

    optToActionMap = { '1' : console.create, '2' : console.load }
    console.repeatedOptRead(optToActionMap)

    deinit()
