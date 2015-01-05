from BaseController import BaseController
import tornado.ioloop
import tornado.web
import dateutil.parser
from datetime import datetime, timedelta


class CommandsController(BaseController):

    def get(self):
        """Serves a GET request.
        """
        return_data = dict(data=[], timestamp=datetime.now().isoformat())

        server = self.get_argument("server")
        from_date = self.get_argument("from", None)
        to_date = self.get_argument("to", None)

        if not from_date or not to_date:
            end = datetime.now()
            delta = timedelta(seconds=120)
            start = end - delta
        else:
            start = dateutil.parser.parse(from_date)
            end = dateutil.parser.parse(to_date)

        difference = end - start
        # added to support python version < 2.7, otherwise timedelta has
        # total_seconds()
        difference_total_seconds = difference.days * 24 * 3600
        difference_total_seconds += difference.seconds
        difference_total_seconds += difference.microseconds / 1e6

        minutes = difference_total_seconds / 60
        hours = minutes / 60
        seconds = difference_total_seconds

        if hours > 120:
          group_by = "day"
        elif minutes > 120:
          group_by = "hour"
        elif seconds > 120:
          group_by = "minute"
        else:
          group_by = "second"

        combined_data = []
        stats = self.stats_provider.get_command_stats(server, start, end,
                                                      group_by)
        for data in stats:
            combined_data.append([data[1], data[0]])

        for data in combined_data:
            return_data['data'].append([self.datetime_to_list(data[0]), data[1]])

        self.write(return_data)
