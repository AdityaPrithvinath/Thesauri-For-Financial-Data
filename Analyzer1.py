from utilities import regexExtractor
from utilities import preProcessVocab

class Analyzer1(object):
    # analyzer with one stop-word list - just making stuff up for illustration

    def __init__(self, stopWords):
        self.stopWords = stopWords

    def analyze(self, docId, text):
        regexClean = regexExtractor(str(text))
        tokenizedQueryList = preProcessVocab(regexClean,docId, self.stopWords)
        return tokenizedQueryList