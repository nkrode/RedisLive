#from sqliteprovider import RedisStatsProvider
#from redisprovider import RedisStatsProvider

from api.util.settings import RedisLiveSettings
import sqliteprovider
import redisprovider


class RedisLiveDataProvider(object):

	@staticmethod
	def GetProvider():
		dataStoreType = RedisLiveSettings.GetDataStoreType()

		if dataStoreType=="redis":
			return redisprovider.RedisStatsProvider()
		else:
			return sqliteprovider.RedisStatsProvider()			
			