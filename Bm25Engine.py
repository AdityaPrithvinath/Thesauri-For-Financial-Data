import collections
from utilities import getTopMatches

class Bm25Engine(object):

    def __init__(self, index, n, k, b):
        self.index = index
        self.n = n
        self.k = k
        self.b = b
        self.avrgD = index.getAvrgD()

    
    def getMatchesOld(self, terms):
        '''
        returns a list of top-n matching pairs (doc-id, score)
        ranked by descending scores
        '''
        matches = collections.defaultdict(float)
        for t in terms:
            if (self.index.hasTerm(t) is None):
                continue
            idf = self.index.getIdf(t)
            for entry in self.index.getEntries(t):
                docId = entry["doc-id"]
                tf = entry["tf"]
                d = self.index.getD(docId)
                w = (idf * tf * (1 + self.k)) / (tf + self.k * (1 - self.b + self.b * d / self.avrgD))
                matches[docId] += w
        return getTopMatches([(k, v) for k, v in matches.items()], self.n)


    def getMatchesNew(self, listOfTermsAndScores):
        '''
        returns a list of top-n matching pairs (doc-id, score)
        ranked by descending scores
        '''
        matches = dict()
        numberOfOccurences =  dict()
        for query in listOfTermsAndScores:
            for t in query:
                if self.index.hasTerm(t[0]):
                    idf = self.index.getIdf(t[0])
                    for entry in self.index.getEntries(t[0]):
                        docId = entry["doc-id"]
                        tf = entry["tf"]
                        d = self.index.getD(docId)
                        w = (idf * tf * (1 + self.k)) / (tf + self.k * (1 - self.b + self.b * d / self.avrgD))
                        matchScore = w*t[1]
                        if docId in matches.keys():
                        	totalScore = matches[docId]*numberOfOccurences[docId]
                        	totalScore += matchScore
                        	numberOfOccurences[docId] += 1
                        	newScore = totalScore/numberOfOccurences[docId]
                        	matches[docId] = newScore
                        	'''
                        	totalScore = matches[docId][0]*numberOfOccurences[docId]
                        	totalScore += matchScore
                        	numberOfOccurences[docId] += 1
                        	newScore = totalScore/numberOfOccurences[docId]
                        	matches[docId][0] = newScore
                        	if matches[docId][1] < t[1]:
                        		matches[docId][1] = t[1]
                        	'''
                        else:
                            matches[docId] = matchScore
                            numberOfOccurences[docId] = 1
                            '''
                            matches[docId] = list()
                            matches[docId].append(matchScore)
                            matches[docId].append(t[1])
                            numberOfOccurences[docId] = 1
                            '''
        #print(matches)
        return getTopMatches([(k, v) for k, v in matches.items()], self.n)
        #return matches