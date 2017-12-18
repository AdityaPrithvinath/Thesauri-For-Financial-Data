from utilities import regexExtractor
import nltk
from IndexEntry import IndexEntry
from nltk.stem import WordNetLemmatizer

class SurfaceAnalyzerWithStop(object):
    # analyzer with no stop words - just making stuff up for illustration

    def __init__(self, stopWords):
        self.stopWords = stopWords
        self.lemmatizer = WordNetLemmatizer()

    
    def lemmatizeWord(self, word, posValue):

        # lemmatizer = WordNetLemmatizer()
        
        mapping = {('NN', 'NNS') : 'n', ("RB", "RBR", "RBS") : 'r', ("JJ", "JJR", "JJS") : 'a', ("VB", "VBD", "VBG", "VBN", "VBP", "VBZ") : 'v'}
        posTag = mapping.get(posValue, word)
        if posTag is not word:
            lemmaValue = self.lemmatizer.lemmatize(word, posTag)
        else:
            lemmaValue = self.lemmatizer.lemmatize(word)

        return lemmaValue

    def analyze(self, dataPointName, text):
        # TDOD: text is a string 
        # apply the character filter, tokenization, token filter, etc.
        # return a list of generated tokens

        #parsedOutput = regexExtractor(str(text))
        tokens = nltk.word_tokenize(text.lower())
        posTags = nltk.pos_tag(tokens)
                    
        listOfObjects = []
        k = 0
        for values in posTags:
            lemma = self.lemmatizeWord(values[0], values[1])

            if values[0].lower() in self.stopWords:
                k += 1
                continue
            
            #indexEntryObject = IndexEntry(lemma, values[1], dataPointName, text)
            indexEntryObject = IndexEntry(values[0], values[1], dataPointName)
            listOfObjects.append(indexEntryObject)
        return listOfObjects