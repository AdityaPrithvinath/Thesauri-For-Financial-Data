import sys
import json
import os
import itertools

from Result import Result
from pathlib import Path
from Index import Index
from Bm25Engine import Bm25Engine
from Analyzer1 import Analyzer1
from NaiveSurfaceAnalyzer import NaiveSurfaceAnalyzer
from NaiveLemmaAnalyzer import NaiveLemmaAnalyzer
from utilities import regexExtractor
from BooleanEngine import BooleanEngine
from IndexEntry import IndexEntry 
from TfIdfEngine import TfIdfEngine
from SurfaceAnalyzerWithStop import SurfaceAnalyzerWithStop
from utilities import deserialize
from utilities import loadStopWords
from utilities import jsonExtractor
from utilities import loadConfig
from utilities import loadDocs
from utilities import serialize
from utilities import sentenceMapper
from gensim.models import word2vec



def createAnalyzer(analyzerOptions):
    if (analyzerOptions["type"] == "analyzer-1"):
        print("Analyzer-1")
        stopWords = loadStopWords(analyzerOptions["stop-words-file"])
        return Analyzer1(stopWords)
    elif (analyzerOptions["type"] == "lemma"):
        stopWords = loadStopWords(analyzerOptions["stop-words-file"])
        return NaiveLemmaAnalyzer(stopWords)
    elif (analyzerOptions["type"] == "surface"):
        stopWords = loadStopWords(analyzerOptions["stop-words-file"])
        return SurfaceAnalyzerWithStop(stopWords)
    else:
        return NaiveSurfaceAnalyzer()


def createEngine(engineOptions):
    picklePath = Path(engineOptions["index-file"])
    index = deserialize(os.path.join(str(picklePath), "PICKLE.PKL"))
    if (engineOptions["type"] == "boolean"):
        return BooleanEngine(index)
    elif (engineOptions["type"] == "tf-idf"):
        return TfIdfEngine(index, engineOptions["n"])
    elif (engineOptions["type"] == "bm25"):
        return Bm25Engine(index, engineOptions["n"], engineOptions["k"], engineOptions["b"])
    else:
        raise ValueError("bad engine option")


def runInputSearchPrintLoop(engine, analyzer, config):
    resultDict = {}
    model = word2vec.Word2Vec.load(config["w2v-model"]["model-file-location"])

    inputStr = input("\n\t\tEnter search keywords here.  Or Enter 'exit' to terminate: ")
    if inputStr.lower() == "exit":
        sys.exit(0)
    terms = analyzer.analyze("DUMMY", inputStr)
    synonyms = list()
    for term in terms:
        synonymTermVectors = model.most_similar(term.getForm().lower(), topn=5)
        synonymTermVectors.append((term.getForm().lower(),1.0))
        synonyms.append(synonymTermVectors)
    matchesFull = list()
    lsitOfPossibleSearches = list(itertools.product(*synonyms))
    #engine.getMatchesNew(lsitOfPossibleSearches)
    matches = engine.getMatchesNew(lsitOfPossibleSearches)
    for item in matches:
        matchesFull.append(item)
    print(matchesFull)
    resultDict["input"] = inputStr
    resultDict["matches"] = matchesFull
    print(resultDict)
    return resultDict

def runInputSearchPrintLoopOld(engine, analyzer, config):
    termToMatch=[]
    resultDict = {}
    model = word2vec.Word2Vec.load(config["w2v-model"]["model-file-location"])

    inputStr = input("\n\t\tEnter search keywords here.  Or Enter 'exit' to terminate: ")
    if inputStr.lower() == "exit":
        sys.exit(0)
    terms = analyzer.analyze("DUMMY", inputStr)
    for term in terms:
        termToMatch.append(term.getForm().lower())

    matches = engine.getMatchesOld(termToMatch)
    resultDict["input"] = inputStr
    resultDict["matches"] = matches
    return resultDict

def index(config):
    analyzer = createAnalyzer(config["analyzer-options"])
    mappedSentences = loadDocs(config["docs-file"])  # TODO implement loadDocs()
    w2pBigramsModelLocation = config["w2p-model"]["W2P-model-file-bigrams"]
    w2pTrigramsModelLocation = config["w2p-model"]["W2P-model-file-trigrams"]

    listOfValues = []
    for dataPoint in mappedSentences.items():
        for sentence in dataPoint[1]:
            for entry in analyzer.analyze(dataPoint[0], sentence):
                listOfValues.append(entry)


    indexDict = {}  # TODO
    docSizeDict = {}  # TODO

    for obj in listOfValues:

        if obj.getDataPoint() not in docSizeDict:
            docSizeDict[obj.getDataPoint()] = 1
        else:
            docSizeDict[obj.getDataPoint()] += 1

        indexTerm = obj.getForm().lower()
        if indexTerm not in indexDict:
            indexDict[indexTerm] = {}
            data = []
            inFileOccurences = {}
            inFileOccurences["doc-id"] = obj.getDataPoint()
            inFileOccurences["tf"] = 1
            data.append(inFileOccurences)
            indexDict[indexTerm] = {}
            indexDict[indexTerm]["data"] = data
        else:
            for row in indexDict.items():
                if row[0] == indexTerm:
                    foundFlag = False
                    for docs in row[1]["data"]:
                        if docs["doc-id"] == obj.getDataPoint():
                            docs["tf"] += 1
                            foundFlag = True
                    if foundFlag is False:
                        newFileOccurences = {}
                        newFileOccurences["doc-id"] = obj.getDataPoint()
                        newFileOccurences["tf"] = 1
                        row[1]["data"].append(newFileOccurences)

    totalDocsSize = len(docSizeDict)
    modifiedIndexDict = indexDict.copy()
    avrgD = len(listOfValues) / totalDocsSize

    import math
    counter = 0
    for entry in indexDict.items():
        for row in entry[1]["data"]:
            docID = row["doc-id"]
            locatedInFileCount = len(entry[1]["data"])
            word = entry[0]
            computedValue = totalDocsSize / (locatedInFileCount + 1)
            idfValue = math.log(computedValue, 10)
        modifiedIndexDict[word]["idf"] = idfValue
        modifiedIndexDict[word]["id"] = counter
        counter += 1
    index = Index(indexDict, docSizeDict, avrgD)

    newIdexedJsonText = json.dumps(indexDict, indent = 4)
    jsonPath = Path(config["engine-options"]["index-json"])
    if not os.path.exists(os.path.join(str(jsonPath))):
        os.makedirs(os.path.join(str(jsonPath)))
    with open(os.path.join(str(jsonPath), "INDEX.JSON"), 'w') as outfile:
        outfile.write(newIdexedJsonText)

    outputIndexPath = config["engine-options"]["index-file"]
    picklePath = Path(outputIndexPath)
    if not os.path.exists(os.path.join(str(picklePath))):
        os.makedirs(os.path.join(str(picklePath)))
    serialize(index, os.path.join(str(picklePath), "PICKLE.PKL"))


def searchWithSynonyms(config):
    analyzer = createAnalyzer(config["analyzer-options"])
    engine = createEngine(config["engine-options"])

    while(True):
        matchList = runInputSearchPrintLoop(engine, analyzer, config)
        resultList = []
        jsonTextDpDocs = jsonExtractor(config["docs-file"])

        for match in matchList["matches"]:
            for obj in jsonTextDpDocs:
                if match[0] == obj.get("id"):
                    description = obj.get("description")
                    definition = obj.get("definition")
                    name = obj.get("name")
                    resultList.append(Result(match[0], name, description, definition)) 

        for obj in resultList:
            print("\nDOC = ", obj.getName(), "\nVALUE = ", obj.getIdValue())
            #print("DESCRIPTION = ", obj.getDescription())
            #print("DEFINITION = ", obj.getDefinition())
        print("\nTotal Results returned: " + str(len(resultList)))

        outputPath = Path(config["engine-options"]["output-path"])
        if not os.path.exists(str(outputPath)):
            os.makedirs(os.path.join(str(outputPath)))

        with open(os.path.join(str(outputPath), "OUTPUT.TXT"), 'w') as outfile:
            header = str(config["engine-options"]["type"]) + " " + str(config["analyzer-options"]["type"]) + " RESULTS for " + str(matchList["input"]) + ":"
            outfile.write(str(header))
            outfile.write("\nTotal Results returned: " + str(len(resultList)))
            for obj in resultList:
                doc = obj.getName()
                value = obj.getIdValue()
                descriptionValue = obj.getDescription()
                definitionValue = obj.getDefinition()
                outfile.write("\n\nDOC: " + str(doc))
                outfile.write("\nValue: " + str(value))
                outfile.write("\nDescription: " + str(descriptionValue))
                outfile.write("\nDefinition: " + str(definitionValue))

def searchWithoutSynonyms(config):
    analyzer = createAnalyzer(config["analyzer-options"])
    engine = createEngine(config["engine-options"])

    while(True):
        matchList = runInputSearchPrintLoopOld(engine, analyzer, config)
        resultList = []
        jsonTextDpDocs = jsonExtractor(config["docs-file"])

        for match in matchList["matches"]:
            for obj in jsonTextDpDocs:
                if match[0] == obj.get("id"):
                    description = obj.get("description")
                    definition = obj.get("definition")
                    name = obj.get("name")
                    resultList.append(Result(match[0], name, description, definition)) 

        for obj in resultList:
            print("\nDOC = ", obj.getName(), "\nVALUE = ", obj.getIdValue())
            #print("DESCRIPTION = ", obj.getDescription())
            #print("DEFINITION = ", obj.getDefinition())
        print("\nTotal Results returned: " + str(len(resultList)))

        outputPath = Path(config["engine-options"]["output-path"])
        if not os.path.exists(str(outputPath)):
            os.makedirs(os.path.join(str(outputPath)))

        with open(os.path.join(str(outputPath), "OUTPUT.TXT"), 'w') as outfile:
            header = str(config["engine-options"]["type"]) + " " + str(config["analyzer-options"]["type"]) + " RESULTS for " + str(matchList["input"]) + ":"
            outfile.write(str(header))
            outfile.write("\nTotal Results returned: " + str(len(resultList)))
            for obj in resultList:
                doc = obj.getName()
                value = obj.getIdValue()
                descriptionValue = obj.getDescription()
                definitionValue = obj.getDefinition()
                outfile.write("\n\nDOC: " + str(doc))
                outfile.write("\nValue: " + str(value))
                outfile.write("\nDescription: " + str(descriptionValue))
                outfile.write("\nDefinition: " + str(definitionValue))