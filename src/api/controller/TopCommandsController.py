import tornado.ioloop
import tornado.web
import random
import dateutil.parser
import datetime
from dateutil.relativedelta import relativedelta


from BaseController import BaseController


class TopCommandsController(BaseController):

  def get(self):
    
    returnData = { 
                    "data" :  [] 
                  , "timestamp" : datetime.datetime.now().isoformat()
                  }

    server = self.get_argument("server")
    fromDate = self.get_argument("from", None)
    toDate = self.get_argument("to", None)

    if fromDate==None or toDate==None:
      end = datetime.datetime.now()
      delta = datetime.timedelta(seconds=120)
      start = end - delta  
    else:
      start = dateutil.parser.parse(fromDate)
      end   = dateutil.parser.parse(toDate)  

    for data in self.statsProvider.GetTopCommandsStats(server, start, end):
      returnData['data'].append([data[0], data[1]])

    self.write(returnData)