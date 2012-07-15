from decimal import Decimal
from BaseController import BaseController
import tornado.ioloop
import tornado.web
import re


class InfoController(BaseController):
    def get(self):
        """Serves a GET request.
        """
        server = self.get_argument("server")
        redis_info = self.stats_provider.get_info(server)
        databases=[]

        for key in sorted(redis_info.keys()):
            if key.startswith("db"):
                database = redis_info[key]
                database['name']=key
                databases.append(database)

        total_keys=0
        for database in databases:
            total_keys+=database.get("keys")

        if(total_keys==0):
            databases=[{"name" : "db0", "keys" : "0", "expires" : "0"}]

        redis_info['databases'] = databases
        redis_info['total_keys']= self.shorten_number(total_keys)

        uptime_seconds = redis_info['uptime_in_seconds']
        redis_info['uptime'] = self.shorten_time(uptime_seconds)

        commands_processed = redis_info['total_commands_processed']
        commands_processed = self.shorten_number(commands_processed)
        redis_info['total_commands_processed_human'] = commands_processed

        self.write(redis_info)

    def shorten_time(self, seconds):
        """Takes an integer number of seconds and rounds it to a human readable
        format.

        Args:
            seconds (int): Number of seconds to convert.
        """
        if seconds < 60:
            # less than 1 minute
            val = str(seconds) + " sec"
        elif seconds < 3600:
            # if the seconds is less than 1hr
            num = self.rounded_number(seconds, 60)
            if num == "60":
                val = '1h'
            else:
                val = num + "m"
        elif (seconds < 60*60*24):
            # if the number is less than 1 day
            num = self.rounded_number(seconds, 60 * 60)
            if num == "24":
                val = "1d"
            else:
                val = num + "h"
        else:
            num = self.rounded_number(seconds, 60*60*24)
            val = num + "d"

        return val

    def shorten_number(self, number):
        """Shortens a number to a human readable format.

        Args:
            number (int): Number to convert.
        """
        if number < 1000:
            return number
        elif number >= 1000 and number < 1000000:
            num = self.rounded_number(number, 1000)
            val = "1M" if num == "1000" else num + "K"
            return val
        elif number >= 1000000 and number < 1000000000:
            num = self.rounded_number(number, 1000000)
            val = "1B" if num=="1000" else  num + "M"
            return val
        elif number >= 1000000000 and number < 1000000000000:
            num = self.rounded_number(number, 1000000000)
            val = "1T" if num=="1000" else num + "B"
            return val
        else:
            num = self.rounded_number(number, 1000000000000)
            return num + "T"

    def rounded_number(self, number, denominator):
        """Rounds a number.

        Args:
            number (int|float): The number to round.
            denominator (int): The denominator.
        """
        rounded = str(round(Decimal(number)/Decimal(denominator), 1))
        replace_trailing_zero = re.compile('0$')
        no_trailing_zeros = replace_trailing_zero.sub('', rounded)
        replace_trailing_period = re.compile('\.$')
        final_number = replace_trailing_period.sub('', no_trailing_zeros)
        return final_number
