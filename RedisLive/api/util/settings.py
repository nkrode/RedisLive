import json
import os

def get_settings():
    """Parses the settings from redis-live.conf.
    """
    # TODO: Consider YAML. Human writable, machine readable.
    path = os.environ.get("REDIS_LIVE_CONF", os.path.join(os.getcwd(), "redis-live.conf"))
    return json.load(open(path))

def get_redis_servers():
    config = get_settings()
    return config["RedisServers"]

def get_redis_stats_server():
    config = get_settings()
    return config["RedisStatsServer"]

def get_data_store_type():
    config = get_settings()
    return config["DataStoreType"]
