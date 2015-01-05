from BaseController import BaseController
import tornado.ioloop
import tornado.web
import dateutil.parser
import datetime


class MemoryController(BaseController):

    def get(self):
        server = self.get_argument("server")
        from_date = self.get_argument("from", None)
        to_date = self.get_argument("to", None)

        return_data = dict(data=[],
                           timestamp=datetime.datetime.now().isoformat())

        if not from_date or not to_date:
            end = datetime.datetime.now()
            delta = datetime.timedelta(seconds=60)
            start = end - delta
        else:
            start = dateutil.parser.parse(from_date)
            end   = dateutil.parser.parse(to_date)

        combined_data = []
        # TODO: These variables aren't currently used; should they be removed?
        prev_max=0
        prev_current=0
        counter=0

        for data in self.stats_provider.get_memory_info(server, start, end):
            combined_data.append([data[0], data[1], data[2]])

        for data in combined_data:
            d = [self.datetime_to_list(data[0]), data[1], data[2]]
            return_data['data'].append(d)

        self.write(return_data)

