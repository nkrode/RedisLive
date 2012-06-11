import redis
from time import strftime
import time
import random

def monitor():
	redisHost = "127.0.0.1"
	redisPort = 6379
	redisClient = redis.StrictRedis(host=redisHost, port=redisPort, db=0)	
	
	while True:
		x = random.randint(1, 10)
		y = random.randint(1, 100)

		if x==1:
			redisClient.set("string:" + str(y) + ":name","nitin")
		elif x==2:
			redisClient.get("string:" + str(y) + ":name")
		elif x==4:
			redisClient.hset("hash:" + str(y), str(y), str(y))
		else:
			redisClient.setex("string:" + str(y),y,str(y))
		


if __name__ == '__main__':
	monitor()