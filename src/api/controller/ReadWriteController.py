import tornado.ioloop
import tornado.web
import random

from BaseController import BaseController


class ReadWriteController(BaseController):

  def get(self):

    server = self.get_argument("server")
    fromDate = self.get_argument("from", None)
    toDate = self.get_argument("to", None)

    returnData = { "data" :  [] }

    if fromDate == None or toDate == None:       
      for data in self.statsProvider.GetRealTimeMemoryInfo(server):        
        returnData['data'].append([ self.DateTimeToList(data[0]), random.randint(1, 100), random.randint(1, 100)])

    else:
      combinedData = []
      prevMax=0
      prevCurrent=0
      counter=0
      for data in self.statsProvider.GetMemoryInfo(server, fromDate, toDate):
        if counter==0 or prevCurrent!=data[2] or prevMax!=data[1]:
          #combinedData.append([ self.DateTimeToList(data[0]), random.randint(10, 250), random.randint(10, 250)])
          combinedData.append([ data[0], data[1], data[2]])
          counter=counter+1

      combinedData = self.AverageData(combinedData)

      for data in combinedData:
        returnData['data'].append([ self.DateTimeToList(data[0]), data[1], data[2]])

    self.write(returnData)     