class Index(object):

    def __init__(self, indexDict, docSizeDict, avrgD):
        self.indexDict = indexDict
        self.docSizeDict = docSizeDict
        self.avrgD = avrgD

    def getAvrgD(self):
        return self.avrgD

    def getD(self, docId):
        return self.docSizeDict[docId]

    def hasTerm(self, term):
        if term in self.indexDict.keys():
            return True
        else:
            return False

    def getIdf(self, term):
        idf = 0.0
        if (self.hasTerm(term)):
            idf = self.indexDict[term]["idf"]
        return idf

    def getEntries(self, term):
        entries = []
        # print(self.docSizeDict)
        if (self.hasTerm(term)):
            entries = self.indexDict[term]["data"]
        return entries