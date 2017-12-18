class BooleanEngine(object):

    def __init__(self, indexObj):
        self.index = indexObj

    
    def getMatchesOld(self, terms):
        '''
        returns a list of matching pairs (doc-id, score)
        '''
        docIds = {entry["doc-id"] for entry in self.index.getEntries(terms[0])}
        print()
        for t in terms[1:]:
            d = {entry["doc-id"] for entry in self.index.getEntries(t)}
            docIds = docIds & d  # intersection is for AND-search [union would be for OR-search]
        return [(docId, 1.0) for docId in docIds]  # add a constant score of 1.0 to all, for consistency wit the other engines


    def getMatchesNew(self, listOfTermsAndScores):
        '''
        returns a list of matching pairs (doc-id, score)
        '''
        for query in listOfTermsAndScores:
            docIds = {entry["doc-id"] for entry in self.index.getEntries(query[0][0])}
            print()
            for t in query[1:]:
                d = {entry["doc-id"] for entry in self.index.getEntries(t[0])}
                docIds = docIds & d  # intersection is for AND-search [union would be for OR-search]
        return [(docId, 1.0) for docId in docIds]  # add a constant score of 1.0 to all, for consistency wit the other engines