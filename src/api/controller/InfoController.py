import tornado.ioloop
import tornado.web
from decimal import *
import re
from BaseController import BaseController


class InfoController(BaseController):
  def get(self):

    server = self.get_argument("server")

    #redisInfo = self.redisClient.info()
    redisInfo = self.statsProvider.GetInfo(server)
    
    databases=[]
    for key in sorted(redisInfo.keys()):
    	if key.startswith("db"):
    		database = redisInfo[key]
    		database['name']=key
    		databases.append(database)
    
    totalKeys=0
    for database in databases:
    	totalKeys+=database.get("keys")

    if(totalKeys==0):
        databases=[{"name" : "db0", "keys" : "0", "expires" : "0"}]

    redisInfo['databases'] = databases
    redisInfo['total_keys']= self.ShortenNumber(totalKeys)

    uptimeSeconds = redisInfo['uptime_in_seconds']
    redisInfo['uptime'] = self.ShortenTime(uptimeSeconds)

    commandsProcessed = redisInfo['total_commands_processed']
    redisInfo['total_commands_processed_human'] = self.ShortenNumber(commandsProcessed)

    self.write(redisInfo)

  def ShortenTime(self, number):
    numberFormat = '{0}'
    if (number < 60):
      return str(number) + " sec"
    elif (number < 3600):
      num = self.RoundedNumber(number, 60)
      val = "1h" if num=="60" else  num + "m"
      return val
    elif (number < 60*60*24):
      num = self.RoundedNumber(number, 60*60)
      val = "1d" if num=="24" else  num + "h"
      return val
    else:
      num = self.RoundedNumber(number, 60*60*24)
      val = num + "d"
      return val
    
  def ShortenNumber(self, number):
    numberFormat = '{0}'
    if (number < 1000):
      return number
    elif (number >= 1000 and number < 1000000):
      num=self.RoundedNumber(number, 1000)
      val = "1M" if num=="1000" else  num + "K"
      return val
    elif  (number >= 1000000 and number < 1000000000):
      num=self.RoundedNumber(number, 1000000)
      val = "1B" if num=="1000" else  num + "M"
      return val
    elif  (number >= 1000000000 and number < 1000000000000):
      num=self.RoundedNumber(number, 1000000000)
      val = "1T" if num=="1000" else  num + "B"
      return val
    else:
      num=self.RoundedNumber(number, 1000000000000)
      return num + "T"

  def RoundedNumber(self, number, denominator):
    rounded = str(round(Decimal(number)/Decimal(denominator), 1))
    replaceTrailingZero = re.compile('0$')
    noTrailingZeros = replaceTrailingZero.sub('', rounded)
    replaceTrailingPeriod = re.compile('\.$')
    finalNumber = replaceTrailingPeriod.sub('', noTrailingZeros)
    return finalNumber


