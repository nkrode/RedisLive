import datetime
from datetime import date
import redis
import json


class RedisStatsProvider(object):
	""" A Redis based persistance to store and fetch stats data
	"""

	def __init__(self):
		self.server = "localhost"
		self.port = 6381
		self.conn = redis.StrictRedis(host=self.server, port=self.port, db=0)	
	
	
	def SaveMemoryInfo(self, server, datetime, used, peak):
		""" Saves Memory Info
		"""		
		data = { "timestamp" : datetime.strftime('%s'), "used" : used , "peak" : peak }
		self.conn.zadd(server+":memory", datetime.strftime('%s'), data )


	def SaveInfoCommand(self, server, datetime, info):
		""" Save Redis info command dump
		"""
		data = { "timestamp" : datetime.strftime('%s'), "info" : info }
		self.conn.zadd(server+":info", datetime.strftime('%s'), data )

		# c = self.conn.cursor()	
		# c.execute("INSERT INTO info VALUES (\'" + datetime.strftime('%Y-%m-%d %H:%M:%S') + "\',\'" + json.dumps(info) + "\',\'" + server + "\')")
		# self.conn.commit()
		# c.close()

	def SaveKeysInfo(self, server, datetime, expire, persist):
		""" Saves expire vs persist info
		"""
		data = { "timestamp" : datetime.strftime('%s'), "expire" : expire, "persist" : persist }
		self.conn.zadd(server+":keys", datetime.strftime('%s'), data )

		# c = self.conn.cursor()
		# c.execute("INSERT INTO keys VALUES (\'" + datetime.strftime('%Y-%m-%d %H:%M:%S') + "\'," + str(expire) + "," + str(persist) + ",\'" + server + "\')")
		# self.conn.commit()
		# c.close()

	def SaveMonitorCommand(self, server, datetime, command, keyname, argument):
		"Save monitor command"

		# current time
		epoch = datetime.strftime('%s')

		# start a redis MULTI/EXEC transaction
		pipeline = self.conn.pipeline()

		# keep command counts in a sorted set
		# top N commands are easily available from the set		
		commandCountKeyName = server + ":CommandCount:" + epoch		
		pipeline.zincrby(commandCountKeyName, command, 1)

		# keep keys counts in a sorted set
		# top N keys are easily available from the set		
		keyCountKeyName = server + ":KeyCount:" + epoch		
		pipeline.zincrby(keyCountKeyName, keyname, 1)

		# keep aggregate command in a hash
		commandCountKeyName = server + ":CommandCount"		
		pipeline.hincrby(commandCountKeyName, epoch, 1)


		# commit transaction to redis
		pipeline.execute()


		#-----------------------------
		# Another aproach
		#-----------------------------

		# maxCommandsExpected = 100000
		# epoch = int(datetime.strftime('%s'))	

		# commandSetKeyName = server + ":commands"		
		# commandLockKeyName = server + ":command_lock:" + command + ":" + str(epoch)
		# commandCountKeyName =  server + ":command:" + command

		
		# # make sure only one client adds the actual timestamp, 
		# #by doing SETNX to a temporary key
		# isNotSet = self.conn.setnx(commandLockKeyName, epoch)

		# pipeline = self.conn.pipeline()
		
		# val = float(float(1) / float(maxCommandsExpected))
		# print "epoch = " + str(epoch) 		

		# if isNotSet:
  		#  			val = float(float(epoch) + float(val))
  		#  			pipeline.expire(commandLockKeyName, 10)

   			

  		#  		print "val = " + repr(val)
  		#  		pipeline.zincrby(commandCountKeyName, amount = float(val), value = epoch) 
  		#  		pipeline.execute()

		#data = { "timestamp" : datetime.strftime('%s'), "expire" : expire, "persist" : persist }

		#c = self.conn.cursor()	
		#c.execute("INSERT INTO monitor(datetime, command, keyname, arguments, server) VALUES (\'" + datetime.strftime('%Y-%m-%d %H:%M:%S') + "\',\'" + command + "\',\'" + keyname + "\',\'" + argument + "\',\'" + server + "\')")
		#self.conn.commit()
		#c.close()			



	def GetInfo(self, server):
		info = {}
		c = self.conn.cursor()		
		for row in c.execute("select info from info where server='" + server + "' order by datetime desc limit 1;"):
			info = json.loads(row[0])

		c.close()
		return info	

	def GetMemoryInfo(self, server, fromDate, toDate):
		""" Gets stats for Memory Consumption between a range of dates
		"""				
		
		memoryData = []			

		query = """select  strftime('%Y-%m-%d %H:%M:%S',datetime), max, current from memory 
								where datetime >= '""" + fromDate.strftime('%Y-%m-%d %H:%M:%S')  + """' and datetime <='""" + toDate.strftime('%Y-%m-%d %H:%M:%S')  + """' and server='""" + server + """'
								order by datetime"""
		print query

		c = self.conn.cursor()				
		for row in c.execute(query):
			memoryData.append([row[0], row[1], row[2]])
		c.close()

		return memoryData

	def GetCommandStats(self, server, fromDate, toDate, groupBy):
		""" Gets commands processed per second list in the given date range
		"""

		# if groupBy=="day":	
		# 	query = """select count(*) as total, strftime('%Y-%m-%d',datetime) from monitor 
		# 						where datetime >= '""" + fromDate.strftime('%Y-%m-%d %H:%M:%S')  + """' and datetime <='""" + toDate.strftime('%Y-%m-%d %H:%M:%S')  + """' and server='""" + server + """'
		# 						group by strftime('%Y-%m-%d',datetime)								
		# 						order by datetime desc """
		# elif groupBy=="hour":
		# 	query = """select count(*) as total, strftime('%Y-%m-%d %H',datetime) from monitor 								
		# 						where datetime >= '""" + fromDate.strftime('%Y-%m-%d %H:%M:%S')  + """' and datetime <='""" + toDate.strftime('%Y-%m-%d %H:%M:%S')  + """' and server='""" + server + """'
		# 						group by strftime('%Y-%m-%d %H',datetime) 
		# 						order by datetime desc """
		# elif groupBy=="minute":
		# 	query = """select count(*) as total, strftime('%Y-%m-%d %H:%M',datetime) from monitor 
		# 						where datetime >= '""" + fromDate.strftime('%Y-%m-%d %H:%M:%S')  + """' and datetime <='""" + toDate.strftime('%Y-%m-%d %H:%M:%S')  + """' and server='""" + server + """'
		# 						group by strftime('%Y-%m-%d %H:%M',datetime) 
		# 						order by datetime desc """
		# else:
		# 	query = """select count(*) as total, strftime('%Y-%m-%d %H:%M:%S',datetime) from monitor 
		# 						where datetime >= '""" + fromDate.strftime('%Y-%m-%d %H:%M:%S')  + """' and datetime <='""" + toDate.strftime('%Y-%m-%d %H:%M:%S')  + """' and server='""" + server + """'
		# 						group by strftime('%Y-%m-%d %H:%M:%S',datetime) 
		# 						order by datetime desc """
	
		
		# c = self.conn.cursor()		
		# for row in c.execute(query):
		# 	memoryData.append([row[0], row[1]])
		# c.close()	

		start = int(fromDate.strftime("%s"))
		end = int(toDate.strftime("%s"))		
				
		memoryData = []
		s = []
		for x in range(start, end+1):
			s.append( str(x) )

		counts = self.conn.hmget(server + ":CommandCount", s)
		for x in xrange(0,len(counts)):			
			memoryData.append([ 0 if counts[x]==None else int(counts[x]), datetime.datetime.fromtimestamp(start+x).strftime('%Y-%m-%d %H:%M:%S') ])		

		return reversed(memoryData)

	def GetTopCommandsStats(self, server, fromDate, toDate):
		""" Gets top commands processed 
		"""
		
		start = int(fromDate.strftime("%s"))
		end = int(toDate.strftime("%s"))		
		
		pipeline = self.conn.pipeline()

		# for x in range(start, end+1):
		# 	s = [ "_top_command", server + ":CommandCount:" + str(x) ]
		# 	pipeline.zunionstore("_top_command", s)		
		# pipeline.zrange("_top_command", 0, -1, True, True)
		# pipeline.delete("_top_command")
		# results = pipeline.execute()

		s = []
		for x in range(start, end+1):
			s.append( server + ":CommandCount:" + str(x) )
		
		pipeline.zunionstore("_top_command", s)		
		pipeline.zrange("_top_command", 0, 9, True, True)
		pipeline.delete("_top_command")
		results = pipeline.execute()			

		resultData = []		
		for command, count in results[-2]:
			resultData.append([command, count])

		return reversed(resultData)


	def GetTopKeysStats(self, server, fromDate, toDate):
		""" Gets top commands processed 
		"""

		start = int(fromDate.strftime("%s"))
		end = int(toDate.strftime("%s"))		
		
		pipeline = self.conn.pipeline()

		# for x in range(start, end+1):
		# 	s = [ "_top_keys", server + ":KeyCount:" + str(x) ]
		# 	pipeline.zunionstore("_top_keys", s)		
		# pipeline.zrange("_top_keys", 0, -1, True, True)
		# pipeline.delete("_top_keys")
		# results = pipeline.execute()

		s = []
		for x in range(start, end+1):
			s.append( server + ":KeyCount:" + str(x) )
		
		pipeline.zunionstore("_top_keys", s)		
		pipeline.zrange("_top_keys", 0, 4, True, True)
		pipeline.delete("_top_keys")
		results = pipeline.execute()			

		resultData = []		
		for command, count in results[-2]:
			resultData.append([command, count])

		return resultData













	#
	# not evaluated yet
	#


	

	def GetRealTimeKeysInfo(self, server):
		""" Gets real time stats for Keys
		"""		
		keyData = []		
		c = self.conn.cursor()		
		for row in c.execute("select expire, persist from keys where server = '" + server + "' order by datetime desc limit 1;"):
			keyData.append([row[0], row[1]])

		c.close()
		return keyData

