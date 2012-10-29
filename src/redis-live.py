#! /usr/bin/env python

import tornado.ioloop
import tornado.options
from tornado.options import define, options
import tornado.web

from api.controller.BaseStaticFileHandler import BaseStaticFileHandler

from api.controller.ServerListController import ServerListController
from api.controller.InfoController import InfoController
from api.controller.MemoryController import MemoryController
from api.controller.CommandsController import CommandsController
from api.controller.TopCommandsController import TopCommandsController
from api.controller.TopKeysController import TopKeysController

if __name__ == "__main__":
    define("port", default=8888, help="run on the given port", type=int)
    define("debug", default=0, help="debug mode", type=int)
    tornado.options.parse_command_line()

    # Bootup
    handlers = [
    (r"/api/servers", ServerListController),
    (r"/api/info", InfoController),
    (r"/api/memory", MemoryController),
    (r"/api/commands", CommandsController),
    (r"/api/topcommands", TopCommandsController),
    (r"/api/topkeys", TopKeysController),
    (r"/(.*)", BaseStaticFileHandler, {"path": "www"})
    ]

    server_settings = {'debug': options.debug}
    application = tornado.web.Application(handlers, **server_settings)
    application.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
