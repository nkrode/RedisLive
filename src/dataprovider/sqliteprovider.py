import sqlite3
import json

class RedisStatsProvider(object):
	"A Sqlite based persistance to store and fetch stats"

	def __init__(self):
		self.conn = sqlite3.connect('db/redislive.sqlite')	
	
	def SaveMemoryInfo(self, server, timestamp, used, peak):
		""" Saves Memory Info
		"""
		c = self.conn.cursor()
		c.execute("INSERT INTO memory VALUES (\'" + timestamp.strftime('%Y-%m-%d %H:%M:%S') + "\'," + str(used) + "," + str(peak) + ",\'" + server + "\')")
		self.conn.commit()
		c.close()	

	def SaveInfoCommand(self, server, timestamp, info):
		"Save Redis info command dump"
		c = self.conn.cursor()	
		c.execute("INSERT INTO info VALUES (\'" + timestamp.strftime('%Y-%m-%d %H:%M:%S') + "\',\'" + json.dumps(info) + "\',\'" + server + "\')")
		self.conn.commit()
		c.close()
	
	def SaveMonitorCommand(self, server, timestamp, command, keyname, argument):
		"save information about every command"
		argument = ""
		query = "INSERT INTO monitor(datetime, command, keyname, arguments, server) VALUES (\'" + timestamp.strftime('%Y-%m-%d %H:%M:%S') + "\',\'" + command + "\',\'" + keyname + "\',\'" + argument + "\',\'" + server + "\')"
		c = self.conn.cursor()	
		c.execute(query)
		self.conn.commit()
		c.close()		

	def GetInfo(self, server):
		"Get info about the server"
		info = {}
		c = self.conn.cursor()		
		for row in c.execute("select info from info where server='" + server + "' order by datetime desc limit 1;"):
			info = json.loads(row[0])

		c.close()		
		return info	

	def GetMemoryInfo(self, server, fromDate, toDate):
		"Get stats for Memory Consumption between a range of dates"
		
		memoryData = []			

		query = """select  strftime('%Y-%m-%d %H:%M:%S',datetime), max, current from memory 
								where datetime >= '""" + fromDate.strftime('%Y-%m-%d %H:%M:%S')  + """' and datetime <='""" + toDate.strftime('%Y-%m-%d %H:%M:%S')  + """' and server='""" + server + """'
								order by datetime"""	

		c = self.conn.cursor()				
		for row in c.execute(query):
			memoryData.append([row[0], row[1], row[2]])
		c.close()

		return memoryData

	def GetCommandStats(self, server, fromDate, toDate, groupBy):
		""" Gets commands processed per second list in the given date range
		"""

		if groupBy=="day":	
			query = """select count(*) as total, strftime('%Y-%m-%d',datetime) from monitor 
								where datetime >= '""" + fromDate.strftime('%Y-%m-%d %H:%M:%S')  + """' and datetime <='""" + toDate.strftime('%Y-%m-%d %H:%M:%S')  + """' and server='""" + server + """'
								group by strftime('%Y-%m-%d',datetime)								
								order by datetime desc """
		elif groupBy=="hour":
			query = """select count(*) as total, strftime('%Y-%m-%d %H',datetime) from monitor 								
								where datetime >= '""" + fromDate.strftime('%Y-%m-%d %H:%M:%S')  + """' and datetime <='""" + toDate.strftime('%Y-%m-%d %H:%M:%S')  + """' and server='""" + server + """'
								group by strftime('%Y-%m-%d %H',datetime) 
								order by datetime desc """
		elif groupBy=="minute":
			query = """select count(*) as total, strftime('%Y-%m-%d %H:%M',datetime) from monitor 
								where datetime >= '""" + fromDate.strftime('%Y-%m-%d %H:%M:%S')  + """' and datetime <='""" + toDate.strftime('%Y-%m-%d %H:%M:%S')  + """' and server='""" + server + """'
								group by strftime('%Y-%m-%d %H:%M',datetime) 
								order by datetime desc """
		else:
			query = """select count(*) as total, strftime('%Y-%m-%d %H:%M:%S',datetime) from monitor 
								where datetime >= '""" + fromDate.strftime('%Y-%m-%d %H:%M:%S')  + """' and datetime <='""" + toDate.strftime('%Y-%m-%d %H:%M:%S')  + """' and server='""" + server + """'
								group by strftime('%Y-%m-%d %H:%M:%S',datetime) 
								order by datetime desc """

		memoryData = []
		
		c = self.conn.cursor()		
		for row in c.execute(query):
			memoryData.append([row[0], row[1]])

		c.close()
		return reversed(memoryData)

	def GetTopCommandsStats(self, server, fromDate, toDate):
		""" Gets top commands processed 
		"""

		query = """select command, count(*) as total from monitor 
				where datetime >= '""" + fromDate.strftime('%Y-%m-%d %H:%M:%S') + """' and datetime <='""" + toDate.strftime('%Y-%m-%d %H:%M:%S') + """' and server='""" + server + """'
				group by command order by total				
				"""

		memoryData = []
		
		c = self.conn.cursor()		
		for row in c.execute(query):
			memoryData.append([row[0], row[1]])

		c.close()
		return memoryData

	def GetTopKeysStats(self, server, fromDate, toDate):
		""" Gets top commands processed 
		"""

		query = """select keyname, count(*) as total from monitor 
				where datetime >= '""" + fromDate.strftime('%Y-%m-%d %H:%M:%S') + """' and datetime <='""" + toDate.strftime('%Y-%m-%d %H:%M:%S') + """' and server='""" + server + """'
				group by keyname order by total desc 
				limit 10				
				"""		

		memoryData = []
		
		c = self.conn.cursor()		
		for row in c.execute(query):
			memoryData.append([row[0], row[1]])

		c.close()
		return memoryData

		