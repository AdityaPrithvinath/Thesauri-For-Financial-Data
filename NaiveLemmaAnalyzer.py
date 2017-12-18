from utilities import regexExtractor
from utilities import lemmatizeWord
import nltk
import wordninja
from IndexEntry import IndexEntry
from nltk.stem import WordNetLemmatizer

class NaiveLemmaAnalyzer(object):
    # analyzer with no stop words - just making stuff up for illustration

    def __init__(self, stopWords):
        self.stopWords = stopWords
        self.lemmatizer = WordNetLemmatizer()

    def analyze(self, dataPointName, text):
        # TDOD: text is a string 
        # apply the character filter, tokenization, token filter, etc.
        # return a list of generated tokens
        
        parsedOutput = regexExtractor(str(text))
        tokens = nltk.word_tokenize(parsedOutput.lower())
        posTags = nltk.pos_tag(tokens)
        
        listOfObjects = []
        k=0
        for values in posTags:
            nounList = ["NN", "NNS"]
            adverbList = ["RB", "RBR", "RBS"]
            adjectiveList = ["JJ", "JJR", "JJS"]
            verbList = ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]

            if values[0].lower() in self.stopWords:
                k += 1
                continue
            
            if values[1] in nounList:
                lemma = self.lemmatizer.lemmatize(values[0], 'n')
            elif values[1] in adverbList:
                lemma = self.lemmatizer.lemmatize(values[0], 'r')
            elif values[1] in adjectiveList:
                lemma = self.lemmatizer.lemmatize(values[0], 'a')
            elif values[1] in verbList:
                lemma = self.lemmatizer.lemmatize(values[0], 'v')
            else:
                lemma = self.lemmatizer.lemmatize(values[0])
            
            indexEntryObject = IndexEntry(lemma, values[1], dataPointName)
            # indexEntryObject = IndexEntry(values[0], values[1], dataPointName)
            listOfObjects.append(indexEntryObject)
        return listOfObjects