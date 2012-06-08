import tornado.ioloop
import tornado.web
import random

from BaseController import BaseController


class KeySpaceController(BaseController):

  def get(self):

    server = self.get_argument("server")
    fromDate = self.get_argument("from", None)
    toDate = self.get_argument("to", None)

    returnData = { "data" :  [] }

    if fromDate == None or toDate == None:       
      counter = 0
      for data in self.statsProvider.GetRealTimeMemoryInfo(server):   
        if counter<5:     
          returnData['data'].append([ self.DateTimeToList(data[0]), random.randint(10, 250), random.randint(10, 250)])
          counter=counter+1

    else:
      prevMax=0
      prevCurrent=0
      counter=0
      for data in self.statsProvider.GetMemoryInfo(server, fromDate, toDate):
        if counter==0 or prevCurrent!=data[2] or prevMax!=data[1]:
          returnData['data'].append([ self.DateTimeToList(data[0]), random.randint(10, 250), random.randint(10, 250)])
          counter=counter+1

    self.write(returnData)     