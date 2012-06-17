import tornado.ioloop
import tornado.web
import random

from BaseController import BaseController
from api.util.settings import RedisLiveSettings

class ServerListController(BaseController):

	def get(self):       
		serverList = self.ReadServerConfig()
		servers = { "servers" : serverList }
		self.write(servers)   
		

	def ReadServerConfig(self):
		serverList = []
		redisServers = RedisLiveSettings.GetRedisServers()	

		for server in redisServers:			
			serverList.append({ "server" : server["server"], "port" : server["port"] , "id" : server["server"] + ":" + `server["port"]` })

		return serverList