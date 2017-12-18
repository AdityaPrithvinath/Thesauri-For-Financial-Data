import os
import re
import json
import glob
import itertools

from utilities import sentenceExtractor
from pathlib import Path
from nltk.corpus import wordnet
from utilities import deserialize
from utilities import loadStopWords
from utilities import jsonExtractor

class Synonyms(object):

    def __init__(self, config):
        self.indexLocation = config["engine-options"]['index-file']
        self.phraseLocation = config["engine-options"]['index-json']
        self.synonymLocation = config["corpus-options"]["synonym-destination"]
        self.tcLocation = config["corpus-options"]["training-destination"]


    def synonymReducedPhrases(self):
        corpusPhrasesListCleaned = []
        picklePath = Path(self.indexLocation)
        index = deserialize(os.path.join(picklePath, "PICKLE.PKL"))

        corpusPhrasesPath = Path(os.path.join(self.tcLocation, "TC-phrases-bi-tri.txt"))
        corpusPhrasesList = loadStopWords(corpusPhrasesPath)
        for word in corpusPhrasesList:
            corpusPhrasesListCleaned.append(word.replace("_", " ").lower())

        jsonPhrasePath = Path(self.phraseLocation)
        jsonPhrase = jsonExtractor(os.path.join(jsonPhrasePath, "PHRASE-INDEX.json"))

        synonymsFullJsonPath = Path(self.synonymLocation)
        synonymsFullJson = jsonExtractor(os.path.join(synonymsFullJsonPath, "word-synonyms-wordnet-reduced.json"))

        
        phraseSynonymEntry = {}
        phraseSynonymsList = []

        for phraseEntry in jsonPhrase:

            phraseAllMeanings = []
            encodedPhrase = phraseEntry['encoded-phrase']
            originalPhrase = phraseEntry['original-phrase']
            tokenizedOriginalPhrase = originalPhrase.split()
            tokenInCorpusFlag = False
            for token in tokenizedOriginalPhrase:
                for phrase in corpusPhrasesListCleaned:
                    brokenPhrase = phrase.split()
                    if token.lower() in brokenPhrase:
                        tokenInCorpusFlag = True
                        break

            if tokenInCorpusFlag == False:
                continue


            dpId = phraseEntry['dp-id']
            for encodedId in encodedPhrase:
                for synonymEntry in synonymsFullJson:
                    if synonymEntry['id'] == encodedId:
                        # COMMENT <TAG-001> TO ALLOW EMPTY SYNONYMS FOR SPECIAL CASES LIKE KEYWORDS
                        if len(synonymEntry['synonyms']) == 0:
                            reg = re.compile(r'[^A-Za-z]')
                            substitute = re.sub(reg, ' ', originalPhrase)
                            tokenizedPhraseInput = substitute.split()
                            phraseAllMeanings.append(tokenizedPhraseInput)
                        else:
                        # COMMENT </TAG-001> TO ALLOW EMPTY SYNONYMS FOR SPECIAL CASES LIKE KEYWORDS
                            phraseAllMeanings.append(synonymEntry['synonyms'])

            phraseSynonymEntry['dp-id'] = dpId
            phraseSynonymEntry['synonyms'] = list(itertools.product(*phraseAllMeanings))
            phraseSynonymsList.append(dict(phraseSynonymEntry))

        synonymJsonPath = Path(self.synonymLocation)
        if not os.path.exists(synonymJsonPath):
            os.makedirs(synonymJsonPath)
        phrasesReducedSynonyms = json.dumps(phraseSynonymsList, indent = 4)

        with open(os.path.join(synonymJsonPath, "phrase-synonyms-wordnet-reduced.json"), 'w') as outfile:
            outfile.write(phrasesReducedSynonyms)



    def synonymFullPhrases(self):
        corpusPhrasesListCleaned = []
        picklePath = Path(self.indexLocation)
        index = deserialize(os.path.join(picklePath, "PICKLE.PKL"))

        jsonPhrasePath = Path(self.phraseLocation)
        jsonPhrase = jsonExtractor(os.path.join(jsonPhrasePath, "PHRASE-INDEX.json"))

        synonymsFullJsonPath = Path(self.synonymLocation)
        synonymsFullJson = jsonExtractor(os.path.join(synonymsFullJsonPath, "word-synonyms-wordnet-full.json"))

        
        phraseSynonymEntry = {}
        phraseSynonymsList = []

        for phraseEntry in jsonPhrase:

            phraseAllMeanings = []
            encodedPhrase = phraseEntry['encoded-phrase']
            originalPhrase = phraseEntry['original-phrase']
            dpId = phraseEntry['dp-id']
            for encodedId in encodedPhrase:
                for synonymEntry in synonymsFullJson:
                    if synonymEntry['id'] == encodedId:
                        # COMMENT <TAG-002> TO ALLOW EMPTY SYNONYMS FOR SPECIAL CASES LIKE KEYWORDS
                        if len(synonymEntry['synonyms']) == 0:
                            reg = re.compile(r'[^A-Za-z]')
                            substitute = re.sub(reg, ' ', originalPhrase)
                            tokenizedPhraseInput = substitute.split()
                            phraseAllMeanings.append(tokenizedPhraseInput)
                        else:
                        # COMMENT </TAG-002> TO ALLOW EMPTY SYNONYMS FOR SPECIAL CASES LIKE KEYWORDS
                            phraseAllMeanings.append(synonymEntry['synonyms'])




            phraseSynonymEntry['dp-id'] = dpId
            phraseSynonymEntry['synonyms'] = list(itertools.product(*phraseAllMeanings))
            phraseSynonymsList.append(dict(phraseSynonymEntry))

        synonymJsonPath = Path(self.synonymLocation)
        if not os.path.exists(synonymJsonPath):
            os.makedirs(synonymJsonPath)
        phrasesFullSynonyms = json.dumps(phraseSynonymsList, indent = 4)

        with open(os.path.join(synonymJsonPath, "phrase-synonyms-wordnet-full.json"), 'w') as outfile:
            outfile.write(phrasesFullSynonyms)


    def synonymWords(self):
        uniqueWordsPath = Path(os.path.join(self.tcLocation, "TC-words.txt"))
        uniqueWordsList = loadStopWords(uniqueWordsPath)


        picklePath = Path(self.indexLocation)
        index = deserialize(os.path.join(picklePath, "PICKLE.PKL"))

        wordSynonymFull = []
        wordSynonymReduced = []

        wordSynonymDictionaryFull = {}
        wordSynonymDictionaryReduced = {}


        for entry in index.indexDict.items():
            word = entry[0]
            identifier = entry[1]['id']

            synonymSet = wordnet.synsets(word)
            i = 0
            uniqueSynonyms = set()
            while i < len(synonymSet):
                uniqueSynonyms.add(synonymSet[i].lemmas()[0].name())
                i += 1
                filteredSynonyms = uniqueSynonyms.copy()
            for word in uniqueSynonyms:
                if word not in uniqueWordsList:
                    filteredSynonyms.remove(word)
            
            wordSynonymDictionaryFull['id'] = identifier
            wordSynonymDictionaryFull['synonyms'] = list(uniqueSynonyms)
            wordSynonymFull.append(dict(wordSynonymDictionaryFull))

            wordSynonymDictionaryReduced['id'] = identifier
            wordSynonymDictionaryReduced['synonyms'] = list(filteredSynonyms)
            wordSynonymReduced.append(dict(wordSynonymDictionaryReduced))

        synonymJsonPath = Path(self.synonymLocation)
        synonymFull = json.dumps(wordSynonymFull, indent = 4)
        synonymReduced = json.dumps(wordSynonymReduced, indent = 4)

        if not os.path.exists(synonymJsonPath):
            os.makedirs(synonymJsonPath)


        with open(os.path.join(synonymJsonPath, "word-synonyms-wordnet-full.json"), 'w') as outfile:
            outfile.write(synonymFull)
        with open(os.path.join(synonymJsonPath, "word-synonyms-wordnet-reduced.json"), 'w') as outfile:
            outfile.write(synonymReduced)




