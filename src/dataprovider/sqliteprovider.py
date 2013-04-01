from api.util import settings
import contextlib
import sqlite3
import json

class RedisStatsProvider(object):
    """A Sqlite based persistance to store and fetch stats
    """

    def __init__(self):
        stats = settings.get_sqlite_stats_store()
        self.location = stats.get('path', 'db/redislive.sqlite')
        self.conn = sqlite3.connect(self.location)
        self.retries = 10

    def save_memory_info(self, server, timestamp, used, peak):
        """Saves used and peak memory stats,

        Args:
            server (str): The server ID
            timestamp (datetime): The time of the info.
            used (int): Used memory value.
            peak (int): Peak memory value.
        """
        query = "INSERT INTO memory VALUES (?, ?, ?, ?);"
        values = (timestamp.strftime('%Y-%m-%d %H:%M:%S'), used, peak, server)
        self._retry_query(query, values)

    def save_info_command(self, server, timestamp, info):
        """Save Redis info command dump

        Args:
            server (str): id of server
            timestamp (datetime): Timestamp.
            info (dict): The result of a Redis INFO command.
        """
        query = "INSERT INTO info VALUES (?, ?, ?);"
        values = (timestamp.strftime('%Y-%m-%d %H:%M:%S'), json.dumps(info),
                  server)
        self._retry_query(query, values)

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
        # FIXME: why clear the argument here?
        argument = ""

        query = "INSERT INTO monitor "
        query += "(datetime, command, keyname, arguments, server) "
        query += "VALUES "
        query += "(?, ?, ?, ?, ?);"

        values = (timestamp.strftime('%Y-%m-%d %H:%M:%S'), command, keyname,
                  argument, server)

        self._retry_query(query, values)

    def get_info(self, server):
        """Get info about the server

        Args:
            server (str): The server ID
        """
        with contextlib.closing(self.conn.cursor()) as c:
            query = "SELECT info FROM info WHERE server=?"
            query += "ORDER BY datetime DESC LIMIT 1;"
            for r in c.execute(query, (server,)):
                return(json.loads(r[0]))

    def get_memory_info(self, server, from_date, to_date):
        """Get stats for Memory Consumption between a range of dates

        Args:
            server (str): The server ID
            from_date (datetime): Get memory info from this date onwards.
            to_date (datetime): Get memory info up to this date.
        """
        time_fmt = '%Y-%m-%d %H:%M:%S'
        query = """SELECT strftime('%Y-%m-%d %H:%M:%S', datetime), max, current
        FROM memory
        WHERE datetime >= ?
        AND datetime <= ?
        AND server = ?;"""

        values = (from_date.strftime(time_fmt), to_date.strftime(time_fmt),
                  server)

        with contextlib.closing(self.conn.cursor()) as c:
            return [[r[0], r[1], r[2]] for r in c.execute(query, values)]

    def get_command_stats(self, server, from_date, to_date, group_by):
        """Get total commands processed in the given time period

        Args:
            server (str): The server ID
            from_date (datetime): Get data from this date.
            to_date (datetime): Get data to this date.
            group_by (str): How to group the stats.
        """
        time_fmt = '%Y-%m-%d %H:%M:%S'

        sql = """SELECT COUNT(*) AS total, strftime('%s', datetime)
        FROM monitor
        WHERE datetime >= ?
        AND datetime <= ?
        AND server = ?
        GROUP BY strftime('%s', datetime)
        ORDER BY datetime DESC;"""

        values = (from_date.strftime(time_fmt), to_date.strftime(time_fmt),
                  server)

        if group_by == "day":
            query_time_fmt = '%Y-m-%d'
        elif group_by == "hour":
            query_time_fmt = '%Y-%m-%d %H'
        elif group_by=="minute":
            query_time_fmt = '%Y-%m-%d %H:%M'
        else:
            query_time_fmt = '%Y-%m-%d %H:%M:%S'

        query = sql % (query_time_fmt, query_time_fmt)

        with contextlib.closing(self.conn.cursor()) as c:
            mem_data = [[r[0], r[1]] for r in c.execute(query, values)]
            return reversed(mem_data)

    def get_top_commands_stats(self, server, from_date, to_date):
        """Get top commands processed in the given time period

        Args:
            server (str): Server ID
            from_date (datetime): Get stats from this date.
            to_date (datetime): Get stats to this date.
        """
        time_fmt = '%Y-%m-%d %H:%M:%S'
        query = """SELECT command, COUNT(*) AS total
        FROM monitor
        WHERE datetime >= ?
        AND datetime <= ?
        AND server = ?
        GROUP BY command
        ORDER BY total;"""
        values = (from_date.strftime(time_fmt), to_date.strftime(time_fmt),
                  server)

        with contextlib.closing(self.conn.cursor()) as c:
            return [[r[0], r[1]] for r in c.execute(query, values)]

    def get_top_keys_stats(self, server, from_date, to_date):
        """Gets top comm processed

        Args:
            server (str): Server ID
            from_date (datetime): Get stats from this date.
            to_date (datetime): Get stats to this date.
        """
        time_fmt = '%Y-%m-%d %H:%M:%S'
        query = """SELECT keyname, COUNT(*) AS total
        FROM monitor
        WHERE datetime >= ?
        AND datetime <= ?
        AND server = ?
        GROUP BY keyname ORDER BY total DESC
        LIMIT 10;"""
        values = (from_date.strftime(time_fmt), to_date.strftime(time_fmt),
                  server)

        with contextlib.closing(self.conn.cursor()) as c:
            return [[r[0], r[1]] for r in c.execute(query, values)]

    def _retry_query(self, query, values=None):
        """Run a SQLite query until it sticks or until we reach the max number
        of retries. Single-threaded writes :(

        Args:
            query (str): The query to execute.

        Kwargs:
            values (tuple|dict): Used when the query is parameterized.
        """
        with contextlib.closing(self.conn.cursor()) as cursor:
            completed = False
            counter = 0
            while counter < self.retries and not completed:
                counter += 1
                try:
                    cursor.execute(query, values)
                    self.conn.commit()
                    completed = True
                except Exception:
                    # FIXME: Catch specific exceptions here otherwise it's likely to
                    # mask bugs/issues later.
                    pass
