import os
from gensim.models import word2vec


class MySentences(object):
    def __init__(self, dirname):
        self.dirname = dirname

    def __iter__(self):
        for root, dirs, files in os.walk(self.dirname):
            for file in files:
                for line in open(os.path.join(root, file)):
                    yield line.split()

sentences = MySentences("E:\Python_practice\Mornign_Star_Project\PDF_treatment\Project\CODE\OUTPUTFILES\CorpusSentTokenize")  # a memory-friendly iterator
model = word2vec.Word2Vec(sentences, workers = 4, size = 200, min_count=200, sg=1)
model.save("E:\\Python_practice\\Mornign_Star_Project\\PDF_treatment\\Project\\CODE\\OUTPUTFILES\\W2VmodelCorpusSentTokenize")