import tornado.ioloop
import tornado.web
import redis
import re
import dateutil.parser

from dataprovider.dataprovider import RedisLiveDataProvider
from api.util.RDP import rdp

class BaseController(tornado.web.RequestHandler):

	statsProvider = RedisLiveDataProvider.GetProvider()

	def DateTimeToList(self, datetime):		
		parsedDate = dateutil.parser.parse(datetime)
		return [ parsedDate.year, parsedDate.month, parsedDate.day, parsedDate.hour, parsedDate.minute, parsedDate.second ]

	# todo : fix this
  	def AverageData(self,data):  		
  		average = []

  		deviation=1024*1024
  		
  		start = dateutil.parser.parse(data[0][0])
  		end   = dateutil.parser.parse(data[-1][0])
  		difference = end - start
  		weeks, days = divmod(difference.days, 7)
  		minutes, seconds = divmod(difference.seconds, 60)
		hours, minutes = divmod(minutes, 60)

		if difference.days > 0:
			current_max=0
			current_current=0
			current_d = 0		
			for dt,maxMemory,currentMemory in data:						
				d = dateutil.parser.parse(dt)
				if d.day!=current_d:
					current_d=d.day				
					average.append([dt,maxMemory,currentMemory])
					current_max=maxMemory
					current_current=currentMemory
				else:
					if maxMemory>current_max or currentMemory>current_current:
						average.pop()
						average.append([dt,maxMemory,currentMemory])
						current_max=maxMemory
						current_current=currentMemory
		elif hours > 0:
			current_max=0
			current_current=0
			current = -1	
			keep_flag = False	
			for dt,maxMemory,currentMemory in data:						
				d = dateutil.parser.parse(dt)
				if d.hour!=current:
					current=d.hour				
					average.append([dt,maxMemory,currentMemory])
					current_max=maxMemory
					current_current=currentMemory
					keep_flag=False
				elif abs(maxMemory-current_max)>deviation  or abs(currentMemory-current_current)>deviation :
						#average.pop()
						average.append([dt,maxMemory,currentMemory])
						current_max=maxMemory
						current_current=currentMemory
						keep_flag=True
				elif maxMemory>current_max or currentMemory>current_current :
						if keep_flag!=True:
							average.pop()
						average.append([dt,maxMemory,currentMemory])
						current_max=maxMemory
						current_current=currentMemory
						keep_flag=False
		else:
			current_max=0
			current_current=0
			current_m = -1	
			keep_flag = False	
			for dt,maxMemory,currentMemory in data:						
				d = dateutil.parser.parse(dt)
				if d.minute!=current_m:
					current_m=d.minute				
					average.append([dt,maxMemory,currentMemory])
					current_max=maxMemory
					current_current=currentMemory
					keep_flag=False
				elif abs(maxMemory-current_max)>deviation  or abs(currentMemory-current_current)>deviation :
						#average.pop()
						average.append([dt,maxMemory,currentMemory])
						current_max=maxMemory
						current_current=currentMemory
						keep_flag=True
				elif maxMemory>current_max or currentMemory>current_current :
						if keep_flag!=True:
							average.pop()
						average.append([dt,maxMemory,currentMemory])
						current_max=maxMemory
						current_current=currentMemory
						keep_flag=False



  		return average

  



	
