import redis
from time import strftime
import time

from dataprovider.sqlite import RedisStatsProvider

def monitor():
	redisHost = "127.0.0.1"
	redisPort = 6379
	redisClient = redis.StrictRedis(host=redisHost, port=redisPort, db=0)

	for x in range(0,500000):
		val = x
		if (x % 2 == 0):
			redisClient.set(x,val)
		elif (x % 3 == 0):
			redisClient.get(x-1)
		elif (x % 5 == 0):
			redisClient.hset("customer",x,val)

	# x = 0
	# while True:
	# 	val = x
	# 	x+=1
	# 	if (x % 2 == 0):
	# 		redisClient.set("x:name","nitin")
	# 	elif (x % 3 == 0):
	# 		redisClient.get("x:name")


if __name__ == '__main__':
	monitor()