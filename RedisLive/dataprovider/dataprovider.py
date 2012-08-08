from RedisLive.api.util import settings
import RedisLive.dataprovider.sqliteprovider
import RedisLive.dataprovider.redisprovider


# TODO: Confirm there's not some implementation detail I've missed, then
# ditch the classes here.
class RedisLiveDataProvider(object):

    @staticmethod
    def get_provider():
        """Returns a data provider based on the settings file.

        Valid providers are currently Redis and SQLite.
        """
        data_store_type = settings.get_data_store_type()

        # FIXME: Should use a global variable for "redis" here.
        if data_store_type == "redis":
            return RedisLive.dataprovider.redisprovider.RedisStatsProvider()
        else:
            return RedisLive.dataprovider.sqliteprovider.RedisStatsProvider()
