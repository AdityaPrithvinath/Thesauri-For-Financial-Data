from utilities import regexExtractor
import nltk
from IndexEntry import IndexEntry
from nltk.stem import WordNetLemmatizer

class BaseAnalyzer(object):
    # analyzer with no stop words - just making stuff up for illustration

    def __init__(self):
        pass

    def analyze(self, dataPointName, text):
        # TDOD: text is a string 
        # apply the character filter, tokenization, token filter, etc.
        # return a list of generated tokens

        parsedOutput = regexExtractor(str(text))
        tokens = nltk.word_tokenize(parsedOutput.lower())
        posTags = nltk.pos_tag(tokens)

        listOfObjects = []
        k = 0
        for values in posTags:
            indexEntryObject = IndexEntry(values[0], values[1], dataPointName)
            listOfObjects.append(indexEntryObject)
        return listOfObjects