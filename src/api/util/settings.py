import json
import os
import urlparse
import yaml
# Load settings from the following:
# ENVIRON > yaml > JSON

# load conf
json_config = None
try:
    with open('redis-live.json') as f:
        json_config = json.load(f)
        f.close()
        pass
except IOError:
    try:
        with open('redis-live.conf') as f:
            json_config = json.load(f)
            f.close()
            pass
    except IOError:
        pass

yaml_config = None
try:
    with open('redis-live.yaml') as f:
        yaml_config = yaml.load(f)
        f.close()
        pass
except IOError:
    pass


def parse_redis_url(redis_url):
    _url = urlparse.urlparse(redis_stats_url, scheme="redis")
    _, _, _db = _url.path.rpartition("/")
    _db = int(_db)
    return {
        "host": _url.hostname,
        "port": _url.port,
        "password": _url.password,
        "db": int(_db)
    }

datastore_type = os.environ.get("DATASTORE_TYPE", None)
if datastore_type is None and yaml_config is not None:
    datastore_type = yaml_config.get("DataStoreType", None)
if datastore_type is None and json_config is not None:
    datastore_type = json_config.get("DataStoreType", None)
if datastore_type is None:
    datastore_type = "redis"

DATASTORE_TYPE = datastore_type

redis_stats_server = None
redis_stats_url = os.environ.get("REDIS_STATS_URL", None)
if redis_stats_url is not None:
    redis_stats_server = parse_redis_url(redis_stats_url)
if redis_stats_server is None and yaml_config is not None:
    redis_stats_server = yaml_config.get("RedisStatsServer", None)
if redis_stats_server is None and json_config is not None:
    redis_stats_server = json_config.get("RedisStatsServer", None)
if redis_stats_server is None:
    redis_stats_server = parse_redis_url("redis://localhost:6381/0")

REDIS_STATS_SERVER = redis_stats_server

redis_servers = []
redis_urls = os.environ.get("REDIS_SERVER_URLS", None)
if redis_urls is not None:
    for redis_url in redis_urls.split(","):
        redis_servers.append(parse_redis_url(redis_url))
if len(redis_servers) == 0 and yaml_config is not None:
    redis_servers = yaml_config.get("RedisServers", None)
if len(redis_servers) == 0 and json_config is not None:
    redis_servers = json_config.get("RedisServers", None)
if len(redis_servers) == 0:
    redis_urls = "redis://localhost:6381/0"
    for redis_url in redis_urls.split(","):
        redis_servers.append(parse_redis_url(redis_url))

REDIS_SERVERS = redis_servers
