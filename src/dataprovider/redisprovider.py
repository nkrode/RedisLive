from datetime import date, datetime, timedelta
from dateutil import parser
import redis
import json
import ast

from api.util.settings import RedisLiveSettings

class RedisStatsProvider(object):
	"A Redis based persistance to store and fetch stats"

	def __init__(self):
		# redis server to use to store stats
		statsServer = RedisLiveSettings.GetRedisStatsServer()		
		self.server = statsServer["server"]
		self.port = statsServer["port"]
		self.conn = redis.StrictRedis(host=self.server, port=self.port, db=0)	
	
	def SaveMemoryInfo(self, server, timestamp, used, peak):
		"save used and peak memory stats"		
		data = { "timestamp" : timestamp.strftime('%s'), "used" : used , "peak" : peak }
		self.conn.zadd(server+":memory", timestamp.strftime('%s'), data )

	def SaveInfoCommand(self, server, timestamp, info):
		"Save Redis info command dump"
		self.conn.set(server + ":Info", json.dumps(info))

	def SaveMonitorCommand(self, server, timestamp, command, keyname, argument):
		"save information about every command"	

		epoch = timestamp.strftime('%s')
		currentDate = timestamp.strftime('%y%m%d')
		
		# start a redis MULTI/EXEC transaction
		pipeline = self.conn.pipeline()

		# store top command and key counts in sorted set for every second
		# top N are easily available from sorted set in redis
		# also keep a sorted set for every day
		# switch to daily stats when stats requsted are for a longer time period		
				
		commandCountKeyName = server + ":CommandCount:" + epoch		
		pipeline.zincrby(commandCountKeyName, command, 1)		
		commandCountKeyName = server + ":DailyCommandCount:" + currentDate		
		pipeline.zincrby(commandCountKeyName, command, 1)		
		
		keyCountKeyName = server + ":KeyCount:" + epoch		
		pipeline.zincrby(keyCountKeyName, keyname, 1)		
		keyCountKeyName = server + ":DailyKeyCount:" + currentDate		
		pipeline.zincrby(keyCountKeyName, command, 1)

		# keep aggregate command in a hash
		commandCountKeyName = server + ":CommandCountBySecond"		
		pipeline.hincrby(commandCountKeyName, epoch, 1)

		commandCountKeyName = server + ":CommandCountByMinute"	
		fieldName = currentDate + ":" + str(timestamp.hour) + ":" + str(timestamp.minute)
		pipeline.hincrby(commandCountKeyName, fieldName, 1)

		commandCountKeyName = server + ":CommandCountByHour"	
		fieldName = currentDate + ":" + str(timestamp.hour)
		pipeline.hincrby(commandCountKeyName, fieldName, 1)

		commandCountKeyName = server + ":CommandCountByDay"
		fieldName = currentDate 
		pipeline.hincrby(commandCountKeyName, fieldName, 1)

		# commit transaction to redis
		pipeline.execute()				

	def GetInfo(self, server):
		"Get info about the server"
		info = self.conn.get(server + ":Info")		
		info = json.loads(info)
		return info

	def GetMemoryInfo(self, server, fromDate, toDate):
		"Get stats for Memory Consumption between a range of dates"		
		memoryData = []
		start = int(fromDate.strftime("%s"))
		end = int(toDate.strftime("%s"))		
		rows = self.conn.zrangebyscore(server+":memory", start, end)

		for row in rows:			
			row = ast.literal_eval(row)			
			memoryData.append([datetime.fromtimestamp(int(row['timestamp'])).strftime('%Y-%m-%d %H:%M:%S'),row['peak'], row['used']])		

		return memoryData		

	def GetCommandStats(self, server, fromDate, toDate, groupBy):
		"Get total commands processed in the given time period"
		s = []
		timeStamps = []
		keyName = ""

		if groupBy == "day":
			keyName = server + ":CommandCountByDay"			
			t = fromDate.date()
			while t<= toDate.date():
				s.append(t.strftime('%y%m%d'))
				timeStamps.append(t.strftime('%s'))
				t = t + timedelta(days=1)

		elif groupBy=="hour":
			keyName = server + ":CommandCountByHour"			

			t = fromDate
			while t<= toDate:
				fieldName = t.strftime('%y%m%d') + ":" + str(t.hour)
				s.append(fieldName)
				timeStamps.append(t.strftime('%s'))
				t = t + timedelta(seconds=3600)
			
		elif groupBy=="minute":
			keyName = server + ":CommandCountByMinute"			

			t = fromDate
			while t<= toDate:				
				fieldName = t.strftime('%y%m%d') + ":" + str(t.hour) + ":" + str(t.minute)
				s.append(fieldName)
				timeStamps.append(t.strftime('%s'))
				t = t + timedelta(seconds=60)
			
		else:
			keyName = server + ":CommandCountBySecond"			
			start = int(fromDate.strftime("%s"))
			end = int(toDate.strftime("%s"))		
			for x in range(start, end+1):
				s.append(str(x))
				timeStamps.append(x)

		data = []
		counts = self.conn.hmget(keyName, s)
		for x in xrange(0,len(counts)):			
			if groupBy == "day" :
				data.append([ 0 if counts[x]==None else int(counts[x]), datetime.fromtimestamp(int(timeStamps[x])).strftime('%Y-%m-%d') ])
			if groupBy == "hour" :
				data.append([ 0 if counts[x]==None else int(counts[x]), datetime.fromtimestamp(int(timeStamps[x])).strftime('%Y-%m-%d %H:00:00') ])
			if groupBy == "minute" :
				data.append([ 0 if counts[x]==None else int(counts[x]), datetime.fromtimestamp(int(timeStamps[x])).strftime('%Y-%m-%d %H:%M:00') ])
			else:
				data.append([ 0 if counts[x]==None else int(counts[x]), datetime.fromtimestamp(int(timeStamps[x])).strftime('%Y-%m-%d %H:%M:%S') ])		

		return reversed(data)

	def GetTopCommandsStats(self, server, fromDate, toDate):
		"Get top commands processed in the given time period"
		return reversed(self.GetTopCounts(server, fromDate, toDate, "CommandCount", "DailyCommandCount"))

	def GetTopKeysStats(self, server, fromDate, toDate):
		"Gets top comm processed"
		return self.GetTopCounts(server, fromDate, toDate, "KeyCount", "DailyKeyCount")	


	# Helper methods
	def GetTopCounts(self, server, fromDate, toDate, secondsKeyName, dayKeyName, resultCount=10):
		"""
		Top counts are stored in a sorted set for every second and for every day		
		ZUNIONSTORE across the timeperiods generates the results
		"""

		# get epoch
		start = int(fromDate.strftime("%s"))
		end = int(toDate.strftime("%s"))		
		diff = toDate - fromDate

		# start a redis MULTI/EXEC transaction
		pipeline = self.conn.pipeline()	

		# store the set names to use in ZUNIONSTORE in a list
		s = []		

		if diff.days > 2 :			
			# when difference is over 2 days, no need to check counts for every second
			# Calculate:
			# counts of every second on the start day
			# counts of every day in between
			# counts of every second on the end day

			nextDay = fromDate.date() + timedelta(days=1)
			prevDay = toDate.date() - timedelta(days=1)
			fromDateEndEpoch = int(nextDay.strftime("%s"))-1
			toDateBeginEpoch = int(toDate.date().strftime("%s"))			
			
			# add counts of every second on the start day
			for x in range(start, fromDateEndEpoch+1):
				s.append(server + ":" + secondsKeyName + ":" + str(x))				
			
			# add counts of all days in between
			t = nextDay
			while t<=prevDay:				
				s.append(server + ":" + dayKeyName + ":" + t.strftime('%y%m%d'))
				t = t + timedelta(days=1)
			
			# add counts of every second on the end day
			for x in range(toDateBeginEpoch, end+1):
				s.append(server + ":" + secondsKeyName + ":" + str(x))

		else:
			# add counts of all seconds between start and end date
			for x in range(start, end+1):
				s.append( server + ":" + secondsKeyName + ":" + str(x) )
		
		# store the union of all the sets in a temp set
		tempKeyName = "_top_counts"
		pipeline.zunionstore(tempKeyName, s)		
		pipeline.zrange(tempKeyName, 0, resultCount-1, True, True)		
		pipeline.delete(tempKeyName)

		# commit transaction to redis
		results = pipeline.execute()		

		resultData = []		
		for val, count in results[-2]:
			resultData.append([val, count])

		return resultData






