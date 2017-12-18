from gensim.models import Phrases
from gensim.models.phrases import Phraser
import os
import glob
from pathlib import Path
from utilities import sentenceExtractor
from nltk.tokenize import word_tokenize
from INDEX_AND_ENGINE import  createAnalyzer
import nltk
import json

class TcPhrasesModeller(object):

	def __init__(self, config):
		self.corpusLocation = config["corpus-options"]["Pre-Processed-Corpus-destination"]
		self.trainingLocation = config["corpus-options"]["Analyzed-Corpus-Analysis"]
		self.bigramMinCount = config["w2p-model"]["min-count-bigram"]
		self.thresholdBigram = config["w2p-model"]["threshold-bigram"]
		self.trigramMinCount = config["w2p-model"]["min-count-trigram"]
		self.thresholdTrigram = config["w2p-model"]["threshold-trigram"]
		self.saveLocationBigrams = config["w2p-model"]["W2P-model-file-bigrams"]
		self.saveLocationTrigrams = config["w2p-model"]["W2P-model-file-trigrams"]
		self.AnalyzedCorpus = config["corpus-options"]["Analyzed-Corpus"]
		self.analyzerParam = config["analyzer-options"]
		self.lemmatizer = nltk.WordNetLemmatizer()

	def trigramGenerator(self):
		print("\nExtracting Corpus\n")
		corpusStream = self.sentenceStream()

		if not os.path.exists(os.path.join(self.trainingLocation)):
			os.makedirs(os.path.join(self.trainingLocation))
		
		#####################################################

		print("Building bigrams\n")
		biGramPhrases = Phrases(corpusStream, min_count = self.bigramMinCount, threshold = self.thresholdBigram)
		bigram = Phraser(biGramPhrases)
		bigramSentenceList = (bigram[sentence] for sentence in corpusStream)

		bigramPhraseScore = dict()
		for string, scores in biGramPhrases.export_phrases(corpusStream):
			phrase = string.decode('utf-8')
			if phrase not in bigramPhraseScore.keys():
				bigramPhraseScore[phrase] = scores

		bigramPhraseScoreJson = json.dumps(bigramPhraseScore, indent = 4)
		with open(os.path.join(self.trainingLocation, "bigrams.json"), 'w') as outfile:
			outfile.write(bigramPhraseScoreJson)

		######################################################
		print("Building Trigrams \n")
		triGramPhrases = Phrases(bigramSentenceList, min_count = self.trigramMinCount, threshold = self.thresholdTrigram)
		trigram = Phraser(triGramPhrases)

		trigramPhraseScore = dict()
		for string, scores in triGramPhrases.export_phrases(bigramSentenceList):
			phrase = string.decode('utf-8')
			if phrase not in trigramPhraseScore.keys():
				trigramPhraseScore[phrase] = scores

		trigramPhraseScoreJson = json.dumps(trigramPhraseScore, indent = 4)
		with open(os.path.join(self.trainingLocation, "trigrams.json"), 'w') as outfile:
			outfile.write(trigramPhraseScoreJson)

		location = self.saveLocationBigrams.split('\\')[:-1]
		location = '\\'.join(folders for folders in location)
		if not os.path.exists(os.path.join(location)):
			os.makedirs(os.path.join(location))
		
		########################################################
		print("Saving Model\n")
		bigram.save(os.path.join(self.saveLocationBigrams))
		trigram.save(os.path.join(self.saveLocationTrigrams))

		########################################################
		print("Writing analyzed Files \n")
		#analyzer = createAnalyzer(self.analyzerParam)
		for filepath in glob.iglob(os.path.join(self.corpusLocation, "**", "*.txt"), recursive=True):
			path = Path(filepath)
			file = path.parts[-1]
			directory = path.parts[-2]
			with open(filepath) as inFile:
				sentenceInFile = []
				inputTextStream = self.sentenceStreamFile(inFile)
				bigramSentenceList = (bigram[sentence] for sentence in inputTextStream)
				trigramSentenceList = (trigram[sentence] for sentence in bigramSentenceList)
				
				for sentence in trigramSentenceList:
					posTags = nltk.pos_tag(sentence)
					k=0
					newSentence = []
					for values in posTags:
						nounList = ["NN", "NNS"]
						adverbList = ["RB", "RBR", "RBS"]
						adjectiveList = ["JJ", "JJR", "JJS"]
						verbList = ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]

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

						newSentence.append(lemma)
					
					sentenceInFile.append(newSentence)
            
				if not os.path.exists(os.path.join(self.AnalyzedCorpus, directory)):
					os.makedirs(os.path.join(self.AnalyzedCorpus, directory))
				with open(os.path.join(self.AnalyzedCorpus, directory, file), "a") as outFile:
					for sent in sentenceInFile:
						for word in sent:
							outFile.write(word+' ')
						outFile.write('\n')


	def sentenceStream(self):
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

	def sentenceStreamFile(self, file):
		for lines in file:
			processedLines = sentenceExtractor(lines)
			for line in processedLines.splitlines():
				tokenizedSentence = word_tokenize(line)
				yield tokenizedSentence
