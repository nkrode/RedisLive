from sqliteprovider import RedisStatsProvider
#from redisprovider import RedisStatsProvider

class RedisLiveDataProvider(object):

	@staticmethod
	def GetProvider():
		return RedisStatsProvider()