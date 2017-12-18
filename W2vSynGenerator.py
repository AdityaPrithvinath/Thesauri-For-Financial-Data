from gensim.models import Word2Vec
import nltk
import os
import glob
import re
import json
from INDEX_AND_ENGINE import createAnalyzer
from utilities import loadStopWords
from utilities import jsonExtractor
from utilities import loadConfig
from utilities import loadDocs
from utilities import serialize
from utilities import sentenceMapper
from IndexEntry import IndexEntry
from Analyzer1 import Analyzer1
from NaiveSurfaceAnalyzer import NaiveSurfaceAnalyzer
from NaiveLemmaAnalyzer import NaiveLemmaAnalyzer


class W2vSynGenerator(object):
    def __init__(self, config):
        self.modelFile = config["w2v-model"]["model-file-location"]
        self.indexFile = config["engine-options"]["index-json"]
        self.analyzer = config["analyzer-options"]
        self.outputFile = config["w2v-model"]["synonym-file"]

    def synGenerator(self):
        model = Word2Vec.load(self.modelFile)
        index = jsonExtractor(os.path.join(self.indexFile, "INDEX.JSON"))
        listOfValues = []
        for key, value in index.items():
            listOfValues.append(key)
        synSets = {}
        for word in sorted(listOfValues):
            try:
                if word not in synSets.keys():
                    synSets[word] = model.most_similar(word, topn=10)
            except:
                continue
        synSetsJson = json.dumps(synSets, indent=4)
        if not os.path.exists(self.outputFile):
            os.mkdir(self.outputFile)
        with open(os.path.join(self.outputFile, 'w2vSynonyms.json'), 'w') as outfile:
            outfile.write(synSetsJson)
