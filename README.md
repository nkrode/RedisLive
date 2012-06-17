RedisLive
=========

Visualize your redis instances, analyze query patterns and spikes. 

![Redis Live](https://github.com/kumarnitin/RedisLive/blob/master/design/redis-live.png?raw=true "Redis Live")

Caveat on monitoring redis
==========================

Currently the only hook into monitoring a redis instance is Redis [MONITOR](http://redis.io/commands/monitor) command, which streams back every command processed and hence reduces the throughput of the redis instance. 

Feedback
========

Have feedback, feature request or improvements you'd like to see to RedisLive? Drop me a note [@nkrode](https://twitter.com/#!/nkrode) or just fork and send pull requests!

Authors
-------

**Nitin Kumar**

+ http://twitter.com/nkrode



