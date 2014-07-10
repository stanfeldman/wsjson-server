# -*- coding: utf-8 -*-
from putils.types import Dict
import inspect
from geventwebsocket import WebSocketServer
from werkzeug.wsgi import SharedDataMiddleware
from putils.patterns import Singleton
from router import WsJsonRouter


class WsJsonServer(Singleton):
	def __init__(self, settings):
		self.settings = settings
		self.compile_mapping(settings["mapping"])

	def start(self):
		wsgi_app = WsJsonRouter(self.settings["mapping"])
		wsgi_app = SharedDataMiddleware(wsgi_app, {
			'/': self.settings["files"]
		})
		server = None
		if "ssl" in self.settings:
			ssl_info = self.settings["ssl"]
			if "key" in ssl_info and "cert" in ssl_info:
				server = WebSocketServer((self.settings["application"]["address"], self.settings["application"]["port"]),
					wsgi_app, keyfile=ssl_info["key"], certfile=ssl_info["cert"])
		if not server:
			server = WebSocketServer((self.settings["application"]["address"], self.settings["application"]["port"]), wsgi_app)
		server.serve_forever()

	def compile_mapping(self, mapping):
		mapping = Dict.flat_dict(mapping, start_char="", end_char="")
		new_mapping = []
		for k, v in mapping.iteritems():
			if k[len(k)-2] == "/":
				k = k[:len(k)-2] + k[len(k)-1]
			if k[len(k)-1] == '/':
				k = k.rstrip('/')
			if inspect.isclass(v):
				new_mapping.append((k, v()))
			else:
				new_mapping.append((k, v))
		self.settings["mapping"] = new_mapping





