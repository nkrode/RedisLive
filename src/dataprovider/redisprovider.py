from api.util import settings, timeutils
from datetime import datetime, timedelta
import redis
import json
import ast

class RedisStatsProvider(object):
    """A Redis based persistance to store and fetch stats"""

    def __init__(self):
        # redis server to use to store stats
        stats_server = settings.get_redis_stats_server()
        self.server = stats_server["server"]
        self.port = stats_server["port"]
        self.password = stats_server.get("password")
        self.conn = redis.StrictRedis(host=self.server, port=self.port, db=0, password=self.password)

    def save_memory_info(self, server, timestamp, used, peak):
        """Saves used and peak memory stats,

        Args:
            server (str): The server ID
            timestamp (datetime): The time of the info.
            used (int): Used memory value.
            peak (int): Peak memory value.
        """
        data = {"timestamp": str(timeutils.convert_to_epoch(timestamp)),
                "used": used,
                "peak": peak}
        self.conn.zadd(server + ":memory", str(timeutils.convert_to_epoch(timestamp)), data)

    def save_info_command(self, server, timestamp, info):
        """Save Redis info command dump

        Args:
            server (str): id of server
            timestamp (datetime): Timestamp.
            info (dict): The result of a Redis INFO command.
        """
        self.conn.set(server + ":Info", json.dumps(info))

    def save_monitor_command(self, server, timestamp, command, keyname,
                             argument):
        """save information about every command

        Args:
            server (str): Server ID
            timestamp (datetime): Timestamp.
            command (str): The Redis command used.
            keyname (str): The key the command acted on.
            argument (str): The args sent to the command.
        """

        epoch = str(timeutils.convert_to_epoch(timestamp))
        current_date = timestamp.strftime('%y%m%d')

        # start a redis MULTI/EXEC transaction
        pipeline = self.conn.pipeline()

        # store top command and key counts in sorted set for every second
        # top N are easily available from sorted set in redis
        # also keep a sorted set for every day
        # switch to daily stats when stats requsted are for a longer time period        

        command_count_key = server + ":CommandCount:" + epoch
        pipeline.zincrby(command_count_key, command, 1)

        command_count_key = server + ":DailyCommandCount:" + current_date
        pipeline.zincrby(command_count_key, command, 1)

        key_count_key = server + ":KeyCount:" + epoch
        pipeline.zincrby(key_count_key, keyname, 1)

        key_count_key = server + ":DailyKeyCount:" + current_date
        pipeline.zincrby(key_count_key, keyname, 1)

        # keep aggregate command in a hash
        command_count_key = server + ":CommandCountBySecond"
        pipeline.hincrby(command_count_key, epoch, 1)

        command_count_key = server + ":CommandCountByMinute"
        field_name = current_date + ":" + str(timestamp.hour) + ":"
        field_name += str(timestamp.minute)
        pipeline.hincrby(command_count_key, field_name, 1)

        command_count_key = server + ":CommandCountByHour"
        field_name = current_date + ":" + str(timestamp.hour)
        pipeline.hincrby(command_count_key, field_name, 1)

        command_count_key = server + ":CommandCountByDay"
        field_name = current_date
        pipeline.hincrby(command_count_key, field_name, 1)

        # commit transaction to redis
        pipeline.execute()

    def get_info(self, server):
        """Get info about the server

        Args:
            server (str): The server ID
        """
        info = self.conn.get(server + ":Info")
        # FIXME: If the collector has never been run we get a 500 here. `None`
        # is not a valid type to pass to json.loads.
        info = json.loads(info)
        return info

    def get_memory_info(self, server, from_date, to_date):
        """Get stats for Memory Consumption between a range of dates

        Args:
            server (str): The server ID
            from_date (datetime): Get memory info from this date onwards.
            to_date (datetime): Get memory info up to this date.
        """
        memory_data = []
        start = timeutils.convert_to_epoch(from_date)
        end = timeutils.convert_to_epoch(to_date)
        rows = self.conn.zrangebyscore(server + ":memory", start, end)

        for row in rows:
            # TODO: Check to see if there's not a better way to do this. Using
            # eval feels like it could be wrong/dangerous... but that's just a
            # feeling.
            row = ast.literal_eval(row)
            parts = []

            # convert the timestamp
            timestamp = datetime.fromtimestamp(int(row['timestamp']))
            timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')

            memory_data.append([timestamp, row['peak'], row['used']])

        return memory_data

    def get_command_stats(self, server, from_date, to_date, group_by):
        """Get total commands processed in the given time period

        Args:
            server (str): The server ID
            from_date (datetime): Get data from this date.
            to_date (datetime): Get data to this date.
            group_by (str): How to group the stats.
        """
        s = []
        time_stamps = []
        key_name = ""

        if group_by == "day":
            key_name = server + ":CommandCountByDay"
            t = from_date.date()
            while t <= to_date.date():
                s.append(t.strftime('%y%m%d'))
                time_stamps.append(str(timeutils.convert_to_epoch(t)))
                t = t + timedelta(days=1)

        elif group_by == "hour":
            key_name = server + ":CommandCountByHour"

            t = from_date
            while t<= to_date:
                field_name = t.strftime('%y%m%d') + ":" + str(t.hour)
                s.append(field_name)
                time_stamps.append(str(timeutils.convert_to_epoch(t)))
                t = t + timedelta(seconds=3600)

        elif group_by == "minute":
            key_name = server + ":CommandCountByMinute"

            t = from_date
            while t <= to_date:
                field_name = t.strftime('%y%m%d') + ":" + str(t.hour)
                field_name += ":" + str(t.minute)
                s.append(field_name)
                time_stamps.append(str(timeutils.convert_to_epoch(t)))
                t = t + timedelta(seconds=60)

        else:
            key_name = server + ":CommandCountBySecond"
            start = timeutils.convert_to_epoch(from_date)
            end = timeutils.convert_to_epoch(to_date)
            for x in range(start, end + 1):
                s.append(str(x))
                time_stamps.append(x)

        data = []
        counts = self.conn.hmget(key_name, s)
        for x in xrange(0,len(counts)):
            # the default time format string
            time_fmt = '%Y-%m-%d %H:%M:%S'

            if group_by == "day":
                time_fmt = '%Y-%m-%d'
            elif group_by == "hour":
                time_fmt = '%Y-%m-%d %H:00:00'
            elif group_by == "minute":
                time_fmt = '%Y-%m-%d %H:%M:00'

            # get the count.
            try:
                if counts[x] is not None: 
                    count = int(counts[x])
                else:
                    count = 0
            except Exception as e:
                count = 0

            # convert the timestamp
            timestamp = int(time_stamps[x])
            timestamp = datetime.fromtimestamp(timestamp)
            timestamp = timestamp.strftime(time_fmt)

            # add to the data
            data.append([count, timestamp])
        return reversed(data)

    def get_top_commands_stats(self, server, from_date, to_date):
        """Get top commands processed in the given time period

        Args:
            server (str): Server ID
            from_date (datetime): Get stats from this date.
            to_date (datetime): Get stats to this date.
        """

        counts = self.get_top_counts(server, from_date, to_date, "CommandCount",
                                     "DailyCommandCount")
        return reversed(counts)

    def get_top_keys_stats(self, server, from_date, to_date):
        """Gets top comm processed

        Args:
            server (str): Server ID
            from_date (datetime): Get stats from this date.
            to_date (datetime): Get stats to this date.
        """
        return self.get_top_counts(server, from_date, to_date, "KeyCount",
                                   "DailyKeyCount")


    # Helper methods
    def get_top_counts(self, server, from_date, to_date, seconds_key_name,
                       day_key_name, result_count=None):
        """Top counts are stored in a sorted set for every second and for every
        day. ZUNIONSTORE across the timeperiods generates the results.

        Args:
            server (str): The server ID
            from_date (datetime): Get stats from this date.
            to_date (datetime): Get stats to this date.
            seconds_key_name (str): The key for stats at second resolution.
            day_key_name (str): The key for stats at daily resolution.

        Kwargs:
            result_count (int): The number of results to return. Default: 10
        """
        if result_count is None:
            result_count = 10

        # get epoch
        start = timeutils.convert_to_epoch(from_date)
        end = timeutils.convert_to_epoch(to_date)
        diff = to_date - from_date

        # start a redis MULTI/EXEC transaction
        pipeline = self.conn.pipeline()

        # store the set names to use in ZUNIONSTORE in a list
        s = []

        if diff.days > 2 :
            # when difference is over 2 days, no need to check counts for every second
            # Calculate:
            # counts of every second on the start day
            # counts of every day in between
            # counts of every second on the end day
            next_day = from_date.date() + timedelta(days=1)
            prev_day = to_date.date() - timedelta(days=1)
            from_date_end_epoch = timeutils.convert_to_epoch(next_day) - 1
            to_date_begin_epoch = timeutils.convert_to_epoch(to_date.date())

            # add counts of every second on the start day
            for x in range(start, from_date_end_epoch + 1):
                s.append(":".join([server, seconds_key_name, str(x)]))

            # add counts of all days in between
            t = next_day
            while t <= prev_day:
                s.append(":".join([server, day_key_name, t.strftime('%y%m%d')]))
                t = t + timedelta(days=1)

            # add counts of every second on the end day
            for x in range(to_date_begin_epoch, end + 1):
                s.append(server + ":" + seconds_key_name + ":" + str(x))

        else:
            # add counts of all seconds between start and end date
            for x in range(start, end + 1):
                s.append(server + ":" + seconds_key_name + ":" + str(x))

        # store the union of all the sets in a temp set
        temp_key_name = "_top_counts"
        pipeline.zunionstore(temp_key_name, s)
        pipeline.zrange(temp_key_name, 0, result_count - 1, True, True)
        pipeline.delete(temp_key_name)

        # commit transaction to redis
        results = pipeline.execute()

        result_data = []
        for val, count in results[-2]:
            result_data.append([val, count])

        return result_data