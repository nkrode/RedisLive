from __future__ import with_statement
import json


def get_settings():
    """Parses the settings from redis-live.conf.
    """
    # TODO: Consider YAML. Human writable, machine readable.
    with open("redis-live.conf") as config:
        return json.load(config)


def get_redis_servers():
    config = get_settings()
    return config["RedisServers"]


def get_redis_stats_server():
    config = get_settings()
    return config["RedisStatsServer"]


def get_data_store_type():
    config = get_settings()
    return config["DataStoreType"]


def get_sqlite_stats_store():
    config = get_settings()
    return config["SqliteStatsStore"]
