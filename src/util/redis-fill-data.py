#! /usr/bin/env python

import redis
import random


def monitor():
    redisHost = "127.0.0.1"
    redisPort = 6379
    redisClient = redis.StrictRedis(host=redisHost, port=redisPort, db=0)

    while True:

        x = random.randint(1, 100)
        y = random.randint(1, 20)

        if y == 1:
            for z in xrange(1, x):
                redisClient.set("Key:" + repr(x), x)
        elif y == 2:
            for z in xrange(1, x):
                redisClient.get("Key:" + repr(x))
        elif y == 4:
            for z in xrange(1, x):
                redisClient.hset("HashKey:" + repr(x), x, x)
        elif y == 5:
            for z in xrange(1, (x / 2) + 2):
                redisClient.setex("Key:" + repr(x), 1000, x)
        elif y == 6:
            for z in xrange(1, x):
                redisClient.hexists("HashKey:" + repr(x), y)
        elif y == 7:
            for z in xrange(1, x):
                redisClient.setbit("BitSet:" + repr(x), 1, 1)
        elif y == 8:
            for z in xrange(1, x):
                redisClient.getbit("BitSet:" + repr(x), 1)
        elif y == 9:
            for z in xrange(1, x):
                redisClient.expire("Key:" + repr(x), 2000)
        elif y == 11:
            redisClient.flushall()


if __name__ == '__main__':
    monitor()
