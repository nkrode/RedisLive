import json

class RedisLiveSettings(object):

	@staticmethod
	def GetRedisServers():		
		config = RedisLiveSettings.GetSettings()
		return config["RedisServers"]				

	@staticmethod
	def GetRedisStatsServer():
		config = RedisLiveSettings.GetSettings()
		return config["RedisStatsServer"]

	@staticmethod
	def GetSettings():
		config = open("redis-live.conf")
		return json.loads(config.read())

	@staticmethod
	def GetDataStoreType():
		config = RedisLiveSettings.GetSettings()
		return config["DataStoreType"]
