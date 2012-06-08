import tornado.ioloop
import tornado.web
import random

from BaseController import BaseController


class KeysController(BaseController):
	def get(self):
		server = self.get_argument("server")
		fromDate = self.get_argument("from", None)
		toDate = self.get_argument("to", None)
		keysInfo = { "data" :  [] }

		for data in self.statsProvider.GetRealTimeKeysInfo(server):
			keysInfo['data'].append(["Expires", data[0]])
			keysInfo['data'].append(["Persists", data[1]])
		self.write(keysInfo)