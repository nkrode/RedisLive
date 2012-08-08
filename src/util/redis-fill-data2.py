#! /usr/bin/env python

import redis


def monitor():
    redisHost = "127.0.0.1"
    redisPort = 6381
    redisClient = redis.StrictRedis(host=redisHost, port=redisPort, db=0)

    while True:
        x = 1
        redisClient.set("Key:" + repr(x), x)
        redisClient.set("KeyYU:" + repr(x), x)
        redisClient.set("Key:" + repr(x), x)
        redisClient.set("KeyYU:" + repr(x), x)


if __name__ == '__main__':
    monitor()
