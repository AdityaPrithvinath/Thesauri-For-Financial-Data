import PyPDF2
import os
import glob
import mmap
import numpy as np
import time

from pathlib import Path
from utilities import sentenceExtractor
from INDEX_AND_ENGINE import createAnalyzer
from baseAnalyzer import BaseAnalyzer

from gensim.models import Phrases
from gensim.models.phrases import Phraser
#from nltk.tokenize import word_tokenize


class PreProcess(object):

    def __init__(self, config):
        self.collectionPath = config["corpus-options"]["collection-path"]
        self.corpusDestination = config["corpus-options"]["Pre-Processed-Corpus-destination"]
        self.logPath = config["log-file"]


    def textBreakdown(self):
        analyzer = BaseAnalyzer()
        fileCounter = 0
        print("\n\nTXT COLLECTION = ", self.collectionPath)
        collectionPathText = os.path.join(self.collectionPath, "**", "*.txt")
        for filepath in glob.iglob(collectionPathText, recursive=True):
            # print(filepath)
            with open(filepath) as inFile:
                fileCounter += 1
                for lines in inFile:
                    processedLines = sentenceExtractor(lines)
                    for line in processedLines.splitlines():
                        lineAnalyzed = analyzer.analyze("DUMMY", line)
                        lineAfterAnalyzer = ""
                        for finalToken in lineAnalyzed:
                            lineAfterAnalyzer += " " + finalToken.getForm()
                        if len(lineAfterAnalyzer) == 0:
                            continue
                        path = Path(filepath)
                        file = path.parts[-1]
                        directory = path.parts[-2]
                        if not os.path.exists(os.path.join(self.corpusDestination, directory)):
                            os.makedirs(os.path.join(self.corpusDestination, directory))
                        with open(os.path.join(self.corpusDestination, directory, file), "a") as outFile:
                            if lineAfterAnalyzer.endswith("\n"):
                                lineAfterAnalyzer.replace("\n", "")
                                outFile.write(lineAfterAnalyzer + "\n")
                            else:
                                outFile.write(lineAfterAnalyzer + "\n")
                        
                            '''
                        else:
                            with open(os.path.join(self.corpusDestination, directory, file), "a") as outFile:
                                if lineAfterAnalyzer.endswith('\n'):
                                    lineAfterAnalyzer.replace("\n", "")
                                    outFile.write(lineAfterAnalyzer + "\n")
                                else:
                                    outFile.write(lineAfterAnalyzer + "\n")
                            '''

        print("\nTotal TXT processed = ", fileCounter)


    def pdfBreakdown(self):
        analyzer = BaseAnalyzer()
        fileCounter = 0
        print("\n\nPDF COLLECTION = ", self.collectionPath)
        collectionPathText = os.path.join(self.collectionPath, "**", "*.pdf")
        missedPdf = []
        for filepath in glob.iglob(collectionPathText, recursive=True):
        	try:        		
	            fileCounter += 1
	            print(filepath)
	            pdfFileObj = open(filepath, 'rb')
	            pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
	            pageCount = pdfReader.numPages

	            iterate = 0 
	            while iterate < pageCount:
	                pageObj = pdfReader.getPage(iterate)
	                pdfRawValue = pageObj.extractText()
	                stringValue = str(pdfRawValue)
	                continuousString = stringValue.replace("\n", " ")
	                for lines in continuousString.splitlines():
	                    processedLines = sentenceExtractor(lines)
	                    for line in processedLines.splitlines():
	                        lineAnalyzed = analyzer.analyze("DUMMY", line)
	                        lineAfterAnalyzer = ""
	                        for finalToken in lineAnalyzed:
	                            lineAfterAnalyzer += " " + finalToken.getForm()
	                        if len(lineAfterAnalyzer) == 0:
	                            continue
	                        path = Path(filepath)
	                        file = path.parts[-1] + ".txt"
	                        directory = path.parts[-2]
	                        if not os.path.exists(os.path.join(self.corpusDestination, directory)):
	                            os.makedirs(os.path.join(self.corpusDestination, directory))
	                        with open(os.path.join(self.corpusDestination, directory, file), "a") as outFile:
	                            if lineAfterAnalyzer.endswith("\n"):
	                                lineAfterAnalyzer.replace("\n", "")
	                                outFile.write(lineAfterAnalyzer + "\n")
	                            else:
	                                outFile.write(lineAfterAnalyzer + "\n")
	                        
                            #else:
	                        #    with open(os.path.join(self.corpusDestination, directory, file), "a") as outFile:
	                        #        if lineAfterAnalyzer.endswith('\n'):
	                        #            lineAfterAnalyzer.replace("\n", "")
	                        #            outFile.write(lineAfterAnalyzer + "\n")
	                        #        else:
	                        #            outFile.write(lineAfterAnalyzer + "\n")

	                pdfExtract = sentenceExtractor(pdfRawValue)
	                iterate += 1

	            pdfFileObj.close()
	        except (RuntimeError, TypeError, NameError):
	        	fileCounter += -1
	        	missedPdf.append(filepath)
        finalLogPath = Path(self.logPath)
        #if finalLogPath.exsts():
        if not os.path.exists(os.path.join(str(str(finalLogPath)))):
            os.makedirs(os.path.join(str(finalLogPath)))
        with open(os.path.join(str(finalLogPath), "MISSED_PDF.TXT"), "a") as outFile:
        	for file in missedPdf:
        		outFile.write(str(time.time()) + " " + str(file) + "\n")

        print("\nTotal PDF processed = ", fileCounter)
            