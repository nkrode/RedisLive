RedisLive
---------

Visualize your redis instances, analyze query patterns and spikes.

![Redis Live](https://github.com/kumarnitin/RedisLive/blob/master/design/redis-live.png?raw=true "Redis Live")

Setup Instructions
------------------
#### Installation

Install Dependencies

+ [tornado](https://github.com/facebook/tornado) `pip install tornado`
+ [redis.py](https://github.com/andymccurdy/redis-py) `pip install redis`
+ [python-dateutil](http://labix.org/python-dateutil) `pip install python-dateutil`

You'll also need argparse if you're running Python < 2.7:

+ [argparse](http://code.google.com/p/argparse/) `pip install argparse`


Get RedisLive

+ Clone the repo `git clone https://github.com/kumarnitin/RedisLive.git` , or [download the latest release](https://github.com/kumarnitin/RedisLive/zipball/master)

#### Configuration

+ edit redis-live.conf :
+ update the value of the key `RedisServers` to the redis instances you want to monitor. You can monitor multiple instances by appending more values to the RedisServers list.
+ update the value of the key `RedisStatsServer` to the redis instance you will use to store RedisLive data (this redis instance is different from the redis instances you are monitoring).
+ passwords can be added as an optional parameter for any redis instance

if you don't have a spare redis instance to use to store Redis Live data, then you can configure to use sqlite by changing `"DataStoreType" : "sqlite"`

#### Start RedisLive

+ start the monitoring script `./redis-monitor.py --duration=120` duration is in seconds (see caveat)
+ start the webserver `./redis-live.py`
+ RedisLive is now running @ `http://localhost:8888/index.html`


#### Caveat on monitoring redis

Currently the only hook into monitoring a redis instance is Redis [MONITOR](http://redis.io/commands/monitor) command, which streams back every command processed and reduces the throughput of the redis instance. It is recommended to run redis-monitor with --duration suitable for your redis deployment and scheduling it to run periodically as a cron job.


Authors
-------

**Nitin Kumar**

+ http://twitter.com/nkrode

Contributors
------------
+ [splee](https://github.com/splee) (Lee McFadden)
+ [bialecki](https://github.com/bialecki) (Andrew Bialecki)
+ [reustle](https://github.com/reustle) (Shane Reustle)
+ [markdube](https://github.com/markdube) (Mark Dube)
+ [skreuzer](https://github.com/skreuzer) (Steven Kreuzer)
+ [snikch](https://github.com/snikch) (Mal Curtis)
+ [quiver](https://github.com/quiver) (George)

License
-------
RedisLive is released under the MIT license:
+ www.opensource.org/licenses/MIT
