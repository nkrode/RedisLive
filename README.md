RedisLive
---------

Visualize your redis instances, analyze query patterns and spikes. 

![Redis Live](https://github.com/kumarnitin/RedisLive/blob/master/design/redis-live.png?raw=true "Redis Live")

Quick Start
------------

**Clone the repo** `git clone https://github.com/kumarnitin/RedisLive.git`, or [download the latest release](https://github.com/kumarnitin/RedisLive/zipball/master).


Caveat on monitoring redis
--------------------------

Currently the only hook into monitoring a redis instance is Redis [MONITOR](http://redis.io/commands/monitor) command, which streams back every command processed and reduces the throughput of the redis instance. It is recommended to run redis-monitor with --duration suitable for your redis deployment and scheduling it to run periodically as a cron job.

Feedback
--------

Have feedback, feature request or improvements you'd like to see? Drop me a note [@nkrode](https://twitter.com/#!/nkrode) or just fork and send a pull request :-)

Authors
-------

**Nitin Kumar**

+ http://twitter.com/nkrode

License
-------
RedisLive is released under the MIT license:
+ www.opensource.org/licenses/MIT




