import tornado.ioloop
import tornado.web
import random
import dateutil.parser
import datetime

from BaseController import BaseController


class CommandsController(BaseController):

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

    difference = end - start
    weeks, days = divmod(difference.days, 7)
    minutes, seconds = divmod(difference.seconds, 60)
    hours, minutes = divmod(minutes, 60)

    if difference.days > 0:
      groupBy = "day"
    elif hours > 1:        
      groupBy = "hour"              
    elif hours > 0:
      groupBy = "minute"      
    else:
      groupBy = "second"

    combinedData = []      
    for data in self.statsProvider.GetCommandStats(server, start, end, groupBy):                  
        combinedData.append([ data[1], data[0]])   

    for data in combinedData:
      returnData['data'].append([ self.DateTimeToList(data[0]), data[1]])

    self.write(returnData)     