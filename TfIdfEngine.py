from utilities import getTopMatches

class TfIdfEngine(object):

    def __init__(self, index, n):
        self.index = index
        self.n = n

    
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
                matches[docId] += tf * idf
        return getTopMatches([(k, v) for k, v in matches.items()], self.n)


    def getMatchesNew(self, listOfTermsAndScores):
        '''
        returns a list of top-n matching pairs (doc-id, score)
        ranked by descending scores
        '''
        matches = dict()
        for query in listOfTermsAndScores:
            for t in query:
                if self.index.hasTerm(t[0]):
                    idf = self.index.getIdf(t[0])
                    for entry in self.index.getEntries(t[0]):
                        docId = entry["doc-id"]
                        tf = entry["tf"]
                        tf_idf = tf * idf
                        matchScore = tf_idf * t[1]
                        if docId in matches.keys():
                            matches[docId] += matchScore
                        else:
                            matches[docId] = matchScore
        return getTopMatches([(k, v) for k, v in matches.items()], self.n)