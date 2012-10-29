from BaseController import BaseController
from api.util import settings

class ServerListController(BaseController):

    def get(self):
        servers = {"servers": self.read_server_config()}
        self.write(servers)

    def read_server_config(self):
        """Returns a list of servers with the 'id' field added.
        """
        # TODO: Move this into the settings module so everything benefits.
        server_list = []
        redis_servers = settings.REDIS_SERVERS

        for server in redis_servers:
            server_id = "%(host)s:%(port)s" % server
            s = dict(server=server['host'], port=server['port'], id=server_id)
            server_list.append(s)

        return server_list
