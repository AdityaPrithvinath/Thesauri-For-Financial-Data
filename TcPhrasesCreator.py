from gensim.models import Phrases
from gensim.models.phrases import Phraser
import os
import glob
from utilities import sentenceExtractor
from nltk.tokenize import word_tokenize


class TcPhrasesCreator(object):

	def __init__(self, corpusLocation):
		self.corpusLocation = corpusLocation["corpus-destination"]
		self.trainingLocation = corpusLocation["training-destination"]
		self.bigramMinCount = corpusLocation["min-count-bigram"]
		self.thresholdBigram = corpusLocation["threshold-bigram"]
		self.trigramMinCount = corpusLocation["min-count-trigram"]
		self.thresholdTrigram = corpusLocation["threshold-trigram"]

	def bigramGenerator(self):
		corpusStream = self.sentenceStream()
		phrases = Phrases(corpusStream, min_count = self.bigramMinCount, threshold = self.thresholdBigram)
		bigram = Phraser(phrases)

		inputStream = self.sentenceStream()
		bigramSentenceList = (bigram[sentence] for sentence in inputStream)

		bigramList = set()
		for bigramSentence in bigramSentenceList:
			for item in bigramSentence:
				if "_" in item:
					bigramList.add(item)
		
		print("Number of Unique Bigrams = ", len(bigramList))
		for item in sorted(bigramList):
			if not os.path.exists(self.trainingLocation):
				os.makedirs(self.trainingLocation)
			with open(os.path.join(self.trainingLocation, "TC-phrases-bi.txt"), "a") as outFile:
				outFile.write(item + "\n")



	def trigramGenerator(self):
		corpusStream = self.sentenceStream()
		biGramPhrases = Phrases(corpusStream, min_count = self.bigramMinCount, threshold = self.thresholdBigram)
		bigram = Phraser(biGramPhrases)

		inputStream = self.sentenceStream()
		bigramSentenceList = (bigram[sentence] for sentence in inputStream)

		
		triGramPhrases = Phrases(bigramSentenceList, min_count = self.trigramMinCount, threshold = self.thresholdTrigram)
		trigram = Phraser(triGramPhrases)

		inputStream = self.sentenceStream()
		bigramSentenceList = (bigram[sentence] for sentence in inputStream)
		trigramSentenceList = (trigram[sentence] for sentence in bigramSentenceList)

		trigramList = set()
		for trigramSentence in trigramSentenceList:
			for item in trigramSentence:
				if "_" in item:
					trigramList.add(item)

		print("Number of Unique Trigrams = ", len(trigramList))
		for item in sorted(trigramList):
			if not os.path.exists(self.trainingLocation):
				os.makedirs(self.trainingLocation)
			with open(os.path.join(self.trainingLocation, "TC-phrases-bi-tri.txt"), "a") as outFile:
				outFile.write(item + "\n")
		


	def sentenceStream(self):
		phraseList = set()
		corpusPath = os.path.join(self.corpusLocation, "**", "*.txt")
		fileCounter = 0
		for filepath in glob.iglob(corpusPath, recursive=True):
			with open(filepath) as inFile:
				fileCounter += 1
				for lines in inFile:
					processedLines = sentenceExtractor(lines)
					for line in processedLines.splitlines():
						tokenizedSentence = word_tokenize(line)
						yield tokenizedSentence


