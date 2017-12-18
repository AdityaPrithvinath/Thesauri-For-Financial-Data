import os
import glob
import json
from utilities import regexExtractor
from utilities import sentenceExtractor

from pathlib import Path
import nltk
import wordninja

class evalCorpus(object):
	def __init__(self, config):
		self.collectionPath = config["collection-path"]
		self.DocumentScoresFilePath = config["Corpus-Evaluation"]["Document-Scores"]

	def eval(self):
		splitCount = dict()
		splits = set()
		print("\n\nTXT COLLECTION = ", self.collectionPath)
		collectionPathText = os.path.join(self.collectionPath, "**", "*.txt")
		for filepath in glob.iglob(collectionPathText, recursive=True):
			with open(filepath) as inFile:
				splitCountFile = 0
				CountFile = 0
				for lines in inFile:
					processedLines = sentenceExtractor(lines)
					for line in processedLines.splitlines():
						parsedOutput = regexExtractor(str(line))
						tokensNltk = nltk.word_tokenize(parsedOutput.lower())
						tokensWordninja = wordninja.split(parsedOutput.lower())
						CountFile += len(tokensNltk)
						splitDiff = len(tokensWordninja) - len(tokensNltk)
						splitCountFile += splitDiff
				try:
					splitRatio = splitCountFile/CountFile
				except:
					continue
				splits.add(splitRatio)
				splitCount[filepath] = splitRatio

		splitCountJson = json.dumps(splitCount, indent = 4)
		if not os.path.exists(os.path.join(self.DocumentScoresFilePath)):
			os.makedirs(self.DocumentScoresFilePath)
		with open(os.path.join(self.DocumentScoresFilePath,"splitCountText.json"), 'w') as outfile:
			outfile.write(splitCountJson)