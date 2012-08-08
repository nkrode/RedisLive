#! /usr/bin/env python

import redis
from time import strftime
import time
import random

def monitor():
	redisHost = "127.0.0.1"
	redisPort = 6381
	redisClient = redis.StrictRedis(host=redisHost, port=redisPort, db=0)	
	
	while True:
		x=1
		redisClient.set("Key:" + `x`, x)
		redisClient.set("KeyYU:" + `x`, x)
		redisClient.set("Key:" + `x`, x)
		redisClient.set("KeyYU:" + `x`, x)

if __name__ == '__main__':
	monitor()