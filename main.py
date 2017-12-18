import time
import sys
import os
import json
from utilities import jsonExtractor
from WordStream import WordStream
from W2vSynGenerator import W2vSynGenerator
from INDEX_AND_ENGINE import index
from INDEX_AND_ENGINE import searchWithoutSynonyms
from INDEX_AND_ENGINE import searchWithSynonyms
from TcWordsCreator import TcWordsCreator
from TcPhrasesCreator import TcPhrasesCreator
from Synonyms import Synonyms
from Phrase import Phrase
from TCPhraserModel import TcPhrasesModeller
from MySentences import MySentences
from gensim.models import word2vec
from CorpusEvaluation import evalCorpus


def preProcessedCorpusCreation(config):
    wordStreamObject = WordStream(config)
    txtBreakdownStart = time.time()
    wordStreamObject.textBreakdown()
    txtBreakdownEnd = time.time()
    print("Elapsed time for TXT = ", txtBreakdownEnd - txtBreakdownStart, " seconds")


def tcModelling(config, wordsOrPhrasesParam):
    if (wordsOrPhrasesParam == "wordsBeforeAnalysis"):
        corpus_location = config["corpus-options"]["Pre-Processed-Corpus-destination"]
        corpus_words_location = config["corpus-options"]["Pre-Processed-Corpus-Analysis"]
        tcWordsObject = TcWordsCreator(config)
    elif (wordsOrPhrasesParam == "wordsAfterAnalysis"):
        corpus_location = config["corpus-options"]["Analyzed-Corpus"]
        corpus_words_location = config["corpus-options"]["Analyzed-Corpus-Analysis"]
        tcWordsObject = TcWordsCreator(config)
    elif (wordsOrPhrasesParam == "phrases"):
        tcPhrasesObject = TcPhrasesModeller(config)
        tcPhrasesObject.trigramGenerator()


def word2VecTrain(config):
    sentences = MySentences(config["corpus-options"]["Analyzed-Corpus"])  # a memory-friendly iterator
    model = word2vec.Word2Vec(sentences, workers = config["w2v-model"]["workers"], size = config["w2v-model"]["size"], min_count = config["w2v-model"]["min_count"], sg=1, window = config["w2v-model"]["window"])
    location = config["w2v-model"]["model-file-location"].split('\\')[:-1]
    location = '\\'.join(folders for folders in location)
    if not os.path.exists(os.path.join(location)):
        os.makedirs(os.path.join(location))
    model.save(config["w2v-model"]["model-file-location"])


def word2VecSynGen(config): 
    w2vSynGenObj = W2vSynGenerator(config)
    w2vSynGenObj.synGenerator()

    
def synonymGeneration(config, wordsOrPhrasesParam):
    synonymObject = Synonyms(config)
    
    if (wordsOrPhrasesParam == "words"):        
        synonymObject.synonymWords()
    elif (wordsOrPhrasesParam == "phrases"):
        synonymObject.synonymFullPhrases()
        synonymObject.synonymReducedPhrases()


if __name__ == "__main__":
    doWhat = sys.argv[1]
    config = jsonExtractor(sys.argv[2])
    print("CONFIG = ", config)
    if (doWhat == "Evaluate"):
        CorpusEvaluationStart = time.time()
        evaluation = evalCorpus(config)
        evaluation.eval()
        CorpusEvaluationEnd = time.time()
        totalTimeForCorpusEvaluation = CorpusEvaluationEnd - CorpusEvaluationStart
        print("Elaspsed Time for Corpus Evaluation = ", totalTimeForCorpusEvaluation, "seconds")

    elif (doWhat == "pre-process"):
        corpusCreationStart = time.time()
        preProcessedCorpusCreation(config)
        corpusCreationEnd = time.time()
        totalTimeForCorpus = corpusCreationEnd - corpusCreationStart
        print("Elapsed Time for Corpus Creation = ", totalTimeForCorpus, " seconds")

        tcWordsBeforeGeneratorStart = time.time()
        tcModelling(config, "wordsBeforeAnalysis")
        tcWordsBeforeGeneratorEnd = time.time()
        totalTimeForTCWordsBefore = tcWordsBeforeGeneratorEnd - tcWordsBeforeGeneratorStart
        print("Elapsed time for TC-Words = ", totalTimeForTCWordsBefore, " seconds")

        tcPhrasesGeneratorStart = time.time()
        tcModelling(config, "phrases")
        tcPhrasesGeneratorEnd = time.time()
        totalTimeForTCPhrases = tcPhrasesGeneratorEnd - tcPhrasesGeneratorStart
        print("Elapsed time for TC-Phrases = ", totalTimeForTCPhrases, " seconds")

        tcWordsAfterGeneratorStart = time.time()
        tcModelling(config, "wordsAfterAnalysis")
        tcWordsAfterGeneratorEnd = time.time()
        totalTimeForTCWordsAfter = tcWordsAfterGeneratorEnd - tcWordsAfterGeneratorStart
        print("Elapsed time for TC-Words = ", totalTimeForTCWordsAfter, " seconds")
        
        print("TOTAL TIME = ", totalTimeForCorpus + totalTimeForTCWordsBefore + totalTimeForTCPhrases + totalTimeForTCWordsAfter, " seconds")

    elif (doWhat == "w2vtrain"):
        w2vTrainStart = time.time()
        word2VecTrain(config)
        w2vTrainEnd = time.time()
        totalTimeForW2VTraining = w2vTrainStart - w2vTrainEnd
        print("Elapsed time for Word2Vec Training = ", totalTimeForW2VTraining, " seconds")

    elif (doWhat == "w2vSynGen"):
        w2vSynGenStart = time.time()
        word2VecSynGen(config)
        w2vSynGenEnd = time.time()
        totalTimeForW2VSynGen = w2vSynGenStart - w2vSynGenEnd
        print("Elapsed time for Word2Vec Synonyms Generation = ", totalTimeForW2VSynGen, " seconds")

    elif (doWhat == "index"):
        indexCreationStart = time.time()
        index(config)
        indexCreationEnd = time.time()
        totalTimeForIndexCreation = indexCreationEnd - indexCreationStart
        print("Elapsed time for Index Creation = ", totalTimeForIndexCreation, " seconds")

    elif (doWhat == "searchNew"):
        searchWithSynonyms(config)

    elif (doWhat == "searchOld"):
        searchWithoutSynonyms(config)

    elif (doWhat == "syn"):
        synonymWordsStart = time.time()
        synonymGeneration(config, "words")
        synonymWordsEnd = time.time()
        totalTimeForSynonymsWords = synonymWordsEnd - synonymWordsStart
        print("\t\tElapsed time for Synonyms Words = ", totalTimeForSynonymsWords, " seconds")

        synonymPhrasesStart = time.time()
        synonymGeneration(config, "phrases")
        synonymPhrasesEnd = time.time()
        totalTimeForSynonymsPhrases = synonymPhrasesEnd - synonymPhrasesStart
        print("\t\tElapsed time for Synonyms Phrases = ", totalTimeForSynonymsPhrases, " seconds")

    else:
        raise ValueError("bad doWhat option")
