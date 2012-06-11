import socket
import datetime
import threading
import time
from time import strftime
import redis
import traceback
import datetime


#from dataprovider.sqliteprovider import RedisStatsProvider
from dataprovider.redisprovider import RedisStatsProvider


class Monitor():
    def __init__(self, connection_pool):
        self.connection_pool = connection_pool
        self.connection = None

    def __del__(self):
        try:
            self.reset()
        except:
            pass

    def reset(self):
        if self.connection:
            self.connection_pool.release(self.connection)
            self.connection = None

    def monitor(self):
        if self.connection is None:
            self.connection = self.connection_pool.get_connection('monitor', None)
        self.connection.send_command("monitor")
        return self.listen()

    def parse_response(self):
        return self.connection.read_response()

    def listen(self):
        while True:
            yield self.parse_response()

class MonitorThread(threading.Thread):

	def __init__(self, server, port):
		threading.Thread.__init__(self)
		self.server = server
		self.port = port
		self.id = self.server + ":" + str(self.port)
		self._stop = threading.Event()		

	def stop(self):		
		self._stop.set()

	def stopped(self):
		return self._stop.isSet()

	def run(self):
		
		statsProvider = RedisStatsProvider()
		pool = redis.ConnectionPool(host=self.server, port=self.port, db=0)
		monitor=Monitor(pool)
		commands = monitor.monitor()
		
		for command in commands:
			try:

				parts = command.split(" ")

				if len(parts)==1:
					continue
				
				t = parts[0].strip()							
				epoch = float(t)
				timestamp = datetime.datetime.fromtimestamp(epoch)

				command = parts[1].replace('"','').upper()

				if len(parts)>2:					
					keyname = parts[2].replace('"','').strip()
				else:
					keyname = None

				if len(parts)>3:
					arguments = ""
					for x in xrange(3,len(parts)):
						arguments += " " + parts[x].replace('"','')
					arguments=arguments.strip()					
				else:
					arguments = None

				if command!='INFO' and command!='MONITOR':
					statsProvider.SaveMonitorCommand(self.id, timestamp, command, str(keyname), str(arguments))

			except Exception, e:
				tb = traceback.format_exc()
				print "==============================\n"
				print datetime.datetime.now()
				print tb	
				print command
				print "==============================\n"

			if self.stopped():
				break

class InfoThread(threading.Thread):

	def __init__(self, server, port):
		threading.Thread.__init__(self)
		self.server = server
		self.port = port
		self.id = self.server + ":" + str(self.port)
		self._stop = threading.Event()		

	def stop(self):		
		self._stop.set()

	def stopped(self):
		return self._stop.isSet()

	def run(self):
		
		statsProvider = RedisStatsProvider()	
		redisClient = redis.StrictRedis(host=self.server, port=self.port, db=0)
		
		while not self.stopped():	
			try:		
				redisInfo = redisClient.info()		
				currentTime = datetime.datetime.now()
				used_memory = int(redisInfo['used_memory'])
				peak_memory = int(redisInfo['used_memory_peak'])	
				statsProvider.SaveMemoryInfo(self.id, currentTime, used_memory, peak_memory)
				statsProvider.SaveInfoCommand(self.id, currentTime, redisInfo)	

				# databases=[]
				# for key in sorted(redisInfo.keys()):
				# 	if key.startswith("db"):
				# 		database = redisInfo[key]
				# 		database['name']=key
				# 		databases.append(database)

				# expires=0
				# persists=0
				# for database in databases:
				# 	expires+=database.get("expires")
				# 	persists+=database.get("keys")-database.get("expires")

				# statsProvider.SaveKeysInfo(self.id, currentTime, expires, persists)

				time.sleep(1)

			except Exception, e:
				tb = traceback.format_exc()
				print "==============================\n"
				print datetime.datetime.now()
				print tb				
				print "==============================\n"

def main():		

	redisServers = ReadServerConfig()

	threads = []

	for redisServer in redisServers:
		monitor = MonitorThread(redisServer["server"], redisServer["port"])				
		threads.append(monitor)		
		monitor.setDaemon(True)
		monitor.start()

		info = InfoThread(redisServer["server"], redisServer["port"])		
		threads.append(info)
		info.setDaemon(True)
		info.start()



	try:
		while True: 
			pass
	except (KeyboardInterrupt, SystemExit):
		for t in threads:
			t.stop()

def ReadServerConfig():
	redisServers = []
	f = open("config.ini")
	for line in f:
		if line[0]=="#":
			continue
		parts=line.rstrip('\r\n').split(':')		
		redisServers.append({ "server" : parts[0], "port" : int(parts[1])})

	return redisServers

if __name__ == '__main__':
	main()