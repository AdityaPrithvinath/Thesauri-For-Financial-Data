import PyPDF2
import os
import glob
import mmap
import numpy as np
import time

from baseAnalyzer import BaseAnalyzer
from pathlib import Path
from nltk import sent_tokenize
from utilities import sentenceExtractor
from utilities import jsonExtractor
from INDEX_AND_ENGINE import createAnalyzer


class WordStream(object):

    def __init__(self, config):
        self.collectionPath = config["collection-path"]
        self.corpusDestination = config["corpus-options"]["Pre-Processed-Corpus-destination"]
        self.analyzerParam = config["analyzer-options"]
        self.DataFile = config["Data-File"]

    def textBreakdown(self):
        #analyzer = createAnalyzer(self.analyzerParam)
        analyzer = BaseAnalyzer()
        fileCounter = 0
        dataPaths = jsonExtractor(self.DataFile)
        for path, score in dataPaths.items():
            if score < 0.1374:
                filepath = path
                print(filepath)
                with open(filepath) as inFile:
                    fileCounter += 1
                    for lines in inFile:
                        processedLines = sent_tokenize(lines)
                        for line in processedLines:
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
                            else:
                                with open(os.path.join(self.corpusDestination, directory, file), "a") as outFile:
                                    if lineAfterAnalyzer.endswith('\n'):
                                        lineAfterAnalyzer.replace("\n", "")
                                        outFile.write(lineAfterAnalyzer + "\n")
                                    else:
                                        outFile.write(lineAfterAnalyzer + "\n")
        print("\nTotal TXT processed = ", fileCounter)