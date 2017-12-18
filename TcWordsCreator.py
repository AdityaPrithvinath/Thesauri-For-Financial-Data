import os
import glob
import nltk


class TcWordsCreator(object):

    def __init__(self, config):
        self.corpusLocation = config["corpus-options"]["Pre-Processed-Corpus-destination"]
        self.trainingLocation = config["corpus-options"]["Pre-Processed-Corpus-Analysis"]

        wordList = set()
        print("CORPUS = ", self.corpusLocation)
        print("Corpus Description = ", self.trainingLocation)
        corpusPath = os.path.join(self.corpusLocation, "**", "*.txt")
        fileCounter = 0
        for filepath in glob.iglob(corpusPath, recursive=True):
            with open(filepath) as inFile:
                fileCounter += 1
                for lines in inFile:
                    processedLines = nltk.sent_tokenize(lines)
                    for line in processedLines:
                        for word in nltk.word_tokenize(line):
                            wordList.add(word)


        print("Number of Unique Words = ", len(wordList))
        if not os.path.exists(self.trainingLocation):
            os.makedirs(self.trainingLocation)
        with open(os.path.join(self.trainingLocation, "TC-words.txt"), "w") as outFile:
            for word in sorted(wordList):
                outFile.write(word + "\n")