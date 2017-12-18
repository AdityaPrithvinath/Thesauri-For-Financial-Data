class IndexEntry(object):
    def __init__(self, form, value, dataPoint):
        self.form = form
        self.value = value
        self.dataPoint = dataPoint
        

    def getForm(self):
        #print("FORM = ", self.form)
        return self.form

    def getValue(self):
        return self.value

    def getDataPoint(self):
        return self.dataPoint