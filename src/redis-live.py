#! /usr/bin/env python

import tornado.ioloop
import tornado.options
import tornado.web

from api.controller.BaseStaticFileHandler import BaseStaticFileHandler

from api.controller.ServerListController import ServerListController
from api.controller.InfoController import InfoController
from api.controller.MemoryController import MemoryController
from api.controller.CommandsController import CommandsController
from api.controller.TopCommandsController import TopCommandsController
from api.controller.TopKeysController import TopKeysController


# Bootup
application = tornado.web.Application([
  (r"/api/servers", ServerListController),
  (r"/api/info", InfoController),
  (r"/api/memory", MemoryController),
  (r"/api/commands", CommandsController),
  (r"/api/topcommands", TopCommandsController),
  (r"/api/topkeys", TopKeysController),
  (r"/(.*)", BaseStaticFileHandler, {"path": "www"})
], debug="True")


if __name__ == "__main__":
	tornado.options.parse_command_line()
	application.listen(8888)
	tornado.ioloop.IOLoop.instance().start()
