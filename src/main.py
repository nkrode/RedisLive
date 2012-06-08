import tornado.ioloop
import tornado.web

from api.controller.BaseStaticFileHandler import BaseStaticFileHandler

from api.controller.InfoController import InfoController
from api.controller.MemoryController import MemoryController
from api.controller.KeysController import KeysController
from api.controller.ReadWriteController import ReadWriteController
from api.controller.KeySpaceController import KeySpaceController
from api.controller.ServerListController import ServerListController
from api.controller.CommandsController import CommandsController
from api.controller.TopCommandsController import TopCommandsController
from api.controller.TopKeysController import TopKeysController


# Bootup
application = tornado.web.Application([
  (r"/api/info", InfoController),
  (r"/api/memory", MemoryController), 
  (r"/api/keys", KeysController), 
  (r"/api/readwrite", ReadWriteController), 
  (r"/api/keyspace", KeySpaceController), 
  (r"/api/servers", ServerListController), 
  (r"/api/commands", CommandsController), 
  (r"/api/topcommands", TopCommandsController), 
  (r"/api/topkeys", TopKeysController), 
  (r"/(.*)", BaseStaticFileHandler, {"path": "www"})
], debug="True")


if __name__ == "__main__":
	application.listen(8888)
	tornado.ioloop.IOLoop.instance().start()