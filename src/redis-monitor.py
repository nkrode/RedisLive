#! /usr/bin/env python

from api.util import settings
from dataprovider.dataprovider import RedisLiveDataProvider
from threading import Timer
import redis
import datetime
import threading
import traceback
import argparse
import time


class Monitor(object):
    """Monitors a given Redis server using the MONITOR command.
    """

    def __init__(self, connection_pool):
        """Initializes the Monitor class.

        Args:
            connection_pool (redis.ConnectionPool): Connection pool for the \
                    Redis server to monitor.
        """
        self.connection_pool = connection_pool
        self.connection = None

    def __del__(self):
        try:
            self.reset()
        except:
            pass

    def reset(self):
        """If we have a connection, release it back to the connection pool.
        """
        if self.connection:
            self.connection_pool.release(self.connection)
            self.connection = None

    def monitor(self):
        """Kicks off the monitoring process and returns a generator to read the
        response stream.
        """
        if self.connection is None:
            self.connection = self.connection_pool.get_connection('monitor', None)
        self.connection.send_command("monitor")
        return self.listen()

    def parse_response(self):
        """Parses the most recent responses from the current connection.
        """
        return self.connection.read_response()

    def listen(self):
        """A generator which yields responses from the MONITOR command.
        """
        while True:
            yield self.parse_response()

class MonitorThread(threading.Thread):
    """Runs a thread to execute the MONITOR command against a given Redis server
    and store the resulting aggregated statistics in the configured stats
    provider.
    """

    def __init__(self, server, port, password=None):
        """Initializes a MontitorThread.

        Args:
            server (str): The host name or IP of the Redis server to monitor.
            port (int): The port to contact the Redis server on.

        Kwargs:
            password (str): The password to access the Redis host. Default: None
        """
        super(MonitorThread, self).__init__()
        self.server = server
        self.port = port
        self.password = password
        self.id = self.server + ":" + str(self.port)
        self._stop = threading.Event()

    def stop(self):
        """Stops the thread.
        """
        self._stop.set()

    def stopped(self):
        """Returns True if the thread is stopped, False otherwise.
        """
        return self._stop.is_set()

    def run(self):
        """Runs the thread.
        """
        stats_provider = RedisLiveDataProvider.get_provider()
        pool = redis.ConnectionPool(host=self.server, port=self.port, db=0,
                                    password=self.password)
        monitor = Monitor(pool)
        commands = monitor.monitor()

        for command in commands:
            try:
                parts = command.split(" ")

                if len(parts) == 1:
                    continue

                epoch = float(parts[0].strip())
                timestamp = datetime.datetime.fromtimestamp(epoch)

                # Strip '(db N)' and '[N x.x.x.x:xx]' out of the monitor str
                if (parts[1] == "(db") or (parts[1][0] == "["):
                    parts = [parts[0]] + parts[3:]

                command = parts[1].replace('"', '').upper()

                if len(parts) > 2:
                    keyname = parts[2].replace('"', '').strip()
                else:
                    keyname = None

                if len(parts) > 3:
                    # TODO: This is probably more efficient as a list
                    # comprehension wrapped in " ".join()
                    arguments = ""
                    for x in xrange(3, len(parts)):
                        arguments += " " + parts[x].replace('"', '')
                    arguments = arguments.strip()
                else:
                    arguments = None

                if not command == 'INFO' and not command == 'MONITOR':
                    stats_provider.save_monitor_command(self.id, 
                                                        timestamp, 
                                                        command, 
                                                        str(keyname), 
                                                        str(arguments))

            except Exception, e:
                tb = traceback.format_exc()
                print "==============================\n"
                print datetime.datetime.now()
                print tb
                print command
                print "==============================\n"

            if self.stopped():
                break

class InfoThread(threading.Thread):
    """Runs a thread to execute the INFO command against a given Redis server
    and store the resulting statistics in the configured stats provider.
    """

    def __init__(self, server, port, password=None):
        """Initializes an InfoThread instance.

        Args:
            server (str): The host name of IP of the Redis server to monitor.
            port (int): The port number of the Redis server to monitor.

        Kwargs:
            password (str): The password to access the Redis server. \
                    Default: None
        """
        threading.Thread.__init__(self)
        self.server = server
        self.port = port
        self.password = password
        self.id = self.server + ":" + str(self.port)
        self._stop = threading.Event()

    def stop(self):
        """Stops the thread.
        """
        self._stop.set()

    def stopped(self):
        """Returns True if the thread is stopped, False otherwise.
        """
        return self._stop.is_set()

    def run(self):
        """Does all the work.
        """
        stats_provider = RedisLiveDataProvider.get_provider()
        redis_client = redis.StrictRedis(host=self.server, port=self.port, db=0,
                                        password=self.password)

        # process the results from redis
        while not self.stopped():
            try:
                redis_info = redis_client.info()
                current_time = datetime.datetime.now()
                used_memory = int(redis_info['used_memory'])

                # used_memory_peak not available in older versions of redis
                try:
                    peak_memory = int(redis_info['used_memory_peak'])
                except:
                    peak_memory = used_memory

                stats_provider.save_memory_info(self.id, current_time, 
                                                used_memory, peak_memory)
                stats_provider.save_info_command(self.id, current_time, 
                                                 redis_info)

                # databases=[]
                # for key in sorted(redis_info.keys()):
                #     if key.startswith("db"):
                #         database = redis_info[key]
                #         database['name']=key
                #         databases.append(database)

                # expires=0
                # persists=0
                # for database in databases:
                #     expires+=database.get("expires")
                #     persists+=database.get("keys")-database.get("expires")

                # stats_provider.SaveKeysInfo(self.id, current_time, expires, persists)

                time.sleep(1)

            except Exception, e:
                tb = traceback.format_exc()
                print "==============================\n"
                print datetime.datetime.now()
                print tb
                print "==============================\n"

class RedisMonitor(object):

    def __init__(self):
        self.threads = []
        self.active = True

    def run(self, duration):
        """Monitors all redis servers defined in the config for a certain number
        of seconds.

        Args:
            duration (int): The number of seconds to monitor for.
        """
        redis_servers = settings.get_redis_servers()


        for redis_server in redis_servers:

            redis_password = redis_server.get("password")

            monitor = MonitorThread(redis_server["server"], redis_server["port"], redis_password)
            self.threads.append(monitor)
            monitor.setDaemon(True)
            monitor.start()

            info = InfoThread(redis_server["server"], redis_server["port"], redis_password)
            self.threads.append(info)
            info.setDaemon(True)
            info.start()

        t = Timer(duration, self.stop)
        t.start()

        try:
            while self.active:
                pass
        except (KeyboardInterrupt, SystemExit):
            self.stop()
            t.cancel()

    def stop(self):
        """Stops the monitor and all associated threads.
        """
        if args.quiet==False:
            print "shutting down..."
        for t in self.threads:
                t.stop()
        self.active = False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Monitor redis.')
    parser.add_argument('--duration',
                        type=int,
                        help="duration to run the monitor command (in seconds)",
                        required=True)
    parser.add_argument('--quiet',
                        help="do  not write anything to standard output",
                        required=False,
                        action='store_true')
    args = parser.parse_args()
    duration = args.duration
    monitor = RedisMonitor()
    monitor.run(duration)
