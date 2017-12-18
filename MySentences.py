import os


class MySentences(object):
    def __init__(self, dirname):
        self.dirname = dirname

    def __iter__(self):
        for root, dirs, files in os.walk(self.dirname):
            for file in files:
                for line in open(os.path.join(root, file)):
                    yield line.split()
