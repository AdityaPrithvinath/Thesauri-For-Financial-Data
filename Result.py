class Result(object):
    def __init__(self, idValue, name, definition, description):
        self.idValue = idValue
        self.name = name
        self.definition = definition
        self.description = description

    def getIdValue(self):
        #print("FORM = ", self.form)
        return self.idValue

    def getName(self):
        return self.name

    def getDefinition(self):
        return self.definition

    def getDescription(self):
        return self.description
