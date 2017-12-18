import os 
import json 

from pathlib import Path
from nltk.tokenize import word_tokenize
from utilities import jsonExtractor
from utilities import deserialize


class Phrase(object):

	def __init__(self, config):
		self.docsLocation = config["docs-file"]
		self.indexLocation = config["engine-options"]['index-file']
		self.indexJson = config["engine-options"]['index-json']

	def phraseIndex(self):
		picklePath = Path(self.indexLocation)
		index = deserialize(os.path.join(picklePath, "PICKLE.PKL"))

		entryIdentifier = 0
		phraseEntry = {}
		phraseList = []

		docsPath = Path(self.docsLocation)
		dpDocs = jsonExtractor(docsPath)
		for dataPoint in dpDocs:
			dataPointName = dataPoint['name']
			tokenizedEntry = word_tokenize(dataPointName)
			encodedList = []
			for term in tokenizedEntry:
				for entry in index.indexDict.items():
					word = entry[0]
					if word.lower() == term.lower():
						identifier = entry[1]['id']
						encodedList.append(identifier)
						break
					else:
						continue
			
			phraseEntry['dp-id'] = entryIdentifier
			phraseEntry['original-phrase'] = dataPointName
			phraseEntry['encoded-phrase'] = encodedList
			entryIdentifier += 1
			phraseList.append(dict(phraseEntry))

		phraseObject = json.dumps(phraseList, indent = 4)

		phraseJsonPath = Path(self.indexJson)
		if not os.path.exists(phraseJsonPath):
			os.makedirs(phraseJsonPath)
		with open(os.path.join(phraseJsonPath, "PHRASE-INDEX.json"), 'w') as outfile:
			outfile.write(phraseObject)



						



