import tornado.web

class BaseStaticFileHandler(tornado.web.StaticFileHandler):
	def compute_etag(self):
		return None

	def get_cache_time(self, path, modified, mime_type):
		return None

