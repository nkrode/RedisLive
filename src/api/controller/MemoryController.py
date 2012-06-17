import tornado.ioloop
import tornado.web
import random
import dateutil.parser
import datetime

from BaseController import BaseController


class MemoryController(BaseController):

  def get(self):

    server = self.get_argument("server")
    fromDate = self.get_argument("from", None)
    toDate = self.get_argument("to", None)
    
    returnData = { 
                    "data" :  [] 
                  , "timestamp" : datetime.datetime.now().isoformat()
                  }

    if fromDate==None or toDate==None:                   
      end = datetime.datetime.now()
      delta = datetime.timedelta(seconds=60)
      start = end - delta
    else:
      start = dateutil.parser.parse(fromDate)
      end   = dateutil.parser.parse(toDate)

    combinedData = []
    prevMax=0
    prevCurrent=0
    counter=0
    
    for data in self.statsProvider.GetMemoryInfo(server, start, end):
      combinedData.append([ data[0], data[1], data[2]])

    for data in combinedData:
      returnData['data'].append([ self.DateTimeToList(data[0]), data[1], data[2]])

    self.write(returnData)



