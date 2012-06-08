import tornado.ioloop
import tornado.web
import random

from BaseController import BaseController


class ServerListController(BaseController):

	def get(self):       
		serverList = self.ReadServerConfig()
		servers = { "servers" : serverList}
		self.write(servers)   

	def ReadServerConfig(self):
		redisServers = []
		f = open("config.ini")
		for line in f:
			if line[0]=="#":
				continue
			parts=line.rstrip('\r\n').split(':')		
			redisServers.append({ "server" : parts[0], "port" : int(parts[1]) , "id" : parts[0] + ":" + parts[1]})

		return redisServers