import nltk
import json

from nltk.stem import WordNetLemmatizer
from nltk import ne_chunk
import re
from nltk.stem import PorterStemmer
from nltk.chunk import conlltags2tree, tree2conlltags
from IndexEntry import IndexEntry

def jsonExtractor(filePath):
    source = open(filePath, 'r')
    print("SOURCE = ", source)
    jsonDataPoint = json.load(source)
    return jsonDataPoint


def loadConfig(file):
    config = jsonExtractor(file)
    return config

def loadDocs(filePath):
    jsonTextDpDocs = jsonExtractor(filePath)
    mappedValues = sentenceMapper(jsonTextDpDocs)
    return mappedValues


def serialize(obj, file):
    import pickle
    filehandler = open(file, "wb")
    pickle.dump(obj, filehandler)
    filehandler.close()


def sentenceMapper(jsonObject):
    mappedSentences = {}
    for obj in jsonObject:
        sentenceList = []
        definitionValue = obj.get("definition")
        descriptionValue = obj.get("description")
        idValue = obj.get("id")
        if definitionValue is not None:
            sentenceDefinition = nltk.sent_tokenize(definitionValue)
        if descriptionValue is not None:
            sentenceDescription = nltk.sent_tokenize(descriptionValue)

        sentenceList.append(sentenceDefinition)
        sentenceList.append(sentenceDescription)
        mappedSentences[idValue] = sentenceList
    return mappedSentences

def loadStopWords(file):
    stopWords = []
    loadStopWords = open(file, "r")
    stopWords = loadStopWords.read().split()
    return stopWords

def deserialize(file):
    import pickle
    print("FILE = ", file)
    filehandler = open(file, "rb")
    print("DESERIALIZE FILEHANDLER = ", filehandler)
    obj = pickle.load(filehandler)
    filehandler.close()
    return obj

def getTopMatches(matches, n):
    sortedMatches = sorted(matches, key=lambda tup: tup[1], reverse=True)
    return sortedMatches[:n]

lemmatizer = WordNetLemmatizer()
def lemmatizeWord(word, posTag):
    # Method for Lemmatization
    # Input: word to be lemmatized, corresponding POS Tag of the word
    # Output: lemmatized word, POS Tag    
    return lemmatizer.lemmatize(word, pos=posTag)

def namedEntityRecognition(pos):
    chunkedToken = ne_chunk(pos)
    namedEntity = tree2conlltags(chunkedToken)
    return namedEntity

def sentenceExtractor(text):
	# Built from = https://regex101.com/r/nG1gU7/27
	reg = re.compile(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s')
	processedSentences = re.sub(reg, "\n", text)
	return processedSentences

def regexExtractor(text):
    # Method to remove non-alphabetical characters and spaces
    # Input: Text to be cleaned using Regular Expression
    # Output: Cleaned Text
    NewText = re.sub('\s+',' ', text)
    notAlphanumericRegex = re.compile(r'[^A-Za-z]')
    excludedNotAlphanumeric = notAlphanumericRegex.findall(NewText)
    postNotAlphanumericRegex = re.sub(notAlphanumericRegex, ' ', NewText)
    cleansedText = postNotAlphanumericRegex
    return cleansedText

def preProcessVocab(clean_text,docId, stpWords):
    lemmatizer = WordNetLemmatizer()
    nounList = ["NN", "NNS"]
    adverbList = ["RB", "RBR", "RBS"]
    adjectiveList = ["JJ", "JJR", "JJS"]
    verbList = ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]
    stemmer = PorterStemmer()
    
    dpVocab = []

    sentences = nltk.sent_tokenize(clean_text)
    j = 0
    for sentence in sentences:
        # sentenceNew = splitString(sentence)
        tokenList = nltk.word_tokenize(sentence)
        partOfSpeech = nltk.pos_tag(tokenList)
        neChunkedToken = namedEntityRecognition(partOfSpeech)
        k = 0
        for token in tokenList:
            if token.lower() in stpWords and re.search(r'no+', token.lower()) is None:
                k += 1
                continue
            isNamedEntity = False
            stemValue = stemmer.stem(token)
            posValue = neChunkedToken[k][1]

            if posValue in nounList:
                lemmaValue = lemmatizeWord(token, 'n')
            elif posValue in adverbList:
                lemmaValue = lemmatizeWord(token, 'r')
            elif posValue in adjectiveList:
                lemmaValue = lemmatizeWord(token, 'a')
            elif posValue in verbList:
                lemmaValue = lemmatizeWord(token, 'v')
            else:
                lemmaValue = lemmatizer.lemmatize(token)
            if posValue == 'NNP' or posValue == 'NNPS':
                isNamedEntity = True

            # Creating Vocabulary Entry Object. We can further reduce the JSON
            # Output by removing repeating JSON Objects, which is not
            # implemented yet.
            dpVocab.append(IndexEntry(token,lemmaValue,docId))
            k += 1
        j += 1
    return dpVocab