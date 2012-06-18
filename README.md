RedisLive
---------

Visualize your redis instances, analyze query patterns and spikes. 

![Redis Live](https://github.com/kumarnitin/RedisLive/blob/master/design/redis-live.png?raw=true "Redis Live")

Installation
------------
**Install Dependencies**
+ [tornado](https://github.com/facebook/tornado) `pip install tornado`
+ [redis.py] (https://github.com/andymccurdy/redis-py) `pip install redis`
+ [python-dateutil] (http://labix.org/python-dateutil) `pip install python-dateutil`

You'll also need argparse if you're running Python < 2.7:

+ [argparse] (http://code.google.com/p/argparse/) `pip install argparse`

**Get RedisLive**
+ Clone the repo `git clone https://github.com/kumarnitin/RedisLive.git`, or [download the latest release](https://github.com/kumarnitin/RedisLive/zipball/master)

**Configuration**
+ edit **redis-live.conf** and update the value of the key `RedisServers` to the redis instances you want to monitor. You can monitor multiple instances by appending more values to the RedisServers list.

**Start RedisLive**
+ start the monitoring script `./redis-monitor.py --duration=120` duration is in seconds ([see caveat](#caveat-on-monitoring-redis))
+ start the webserver `./redis-live.py`
+ RedisLive is now running @ `http://localhost:8888/index.html`

**Optional Configuration**
+ if you have a local redis instance, you can switch to a redis backed store to save RedisLive data (preferred and much faster)
  + edit redis.conf provide the server and port for the redis instance you will use to store RedisLive data (this redis instance is different from the redis instances you are monitoring). Change the value of RedisStatsServer key.
  + edit /src/dataprovider/dataprovider.py switch to redisprovider :
      + disable line 1 `#from sqliteprovider import RedisStatsProvider`
      + enable line 2  `from redisprovider import RedisStatsProvider`



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




