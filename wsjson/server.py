# -*- coding: utf-8 -*-
from putils.types import Dict
import inspect
from router import Router
from geventwebsocket import WebSocketServer
from werkzeug.wsgi import SharedDataMiddleware
from putils.patterns import Singleton
import gevent
import signal
from pev import Eventer
import re
import logging
logger = logging.getLogger(__name__)


class Server(Singleton):
	STARTED = "server_started"
	STOPPED = "server_stopped"
	def __init__(self, settings):
		self.settings = settings
		if "events" in self.settings:
			self.eventer = Eventer(self.settings["events"])
		else:
			self.eventer = Eventer()
		self.init_controllers_mapping()

	def start(self):
		wsgi_app = Router(self)
		wsgi_app = SharedDataMiddleware(wsgi_app, {
			'/': self.settings["files"]
		})
		self.server = None
		if "ssl" in self.settings:
			ssl_info = self.settings["ssl"]
			if "key" in ssl_info and "cert" in ssl_info:
				self.server = WebSocketServer((self.settings["application"]["address"], self.settings["application"]["port"]),
					wsgi_app, keyfile=ssl_info["key"], certfile=ssl_info["cert"])
		if not self.server:
			self.server = WebSocketServer((self.settings["application"]["address"], self.settings["application"]["port"]), wsgi_app)
		gevent.signal(signal.SIGTERM, self.stop)
		gevent.signal(signal.SIGINT, self.stop)
		self.eventer.publish(Server.STARTED, self)
		try:
			self.server.serve_forever()
		except Exception, e:
			logger.error("start server error %s", str(e), exc_info=True)

	def stop(self):
		self.eventer.publish(Server.STOPPED)
		self.server.stop()

	def init_controllers_mapping(self):
		controllers_mapping = Dict.flat_dict(self.settings["controllers"], start_char="", end_char="")
		new_controllers_mapping = []
		for k, v in controllers_mapping.iteritems():
			if k[len(k)-2] == "/":
				k = k[:len(k)-2] + k[len(k)-1]
			if k[len(k)-1] == '/':
				k = k.rstrip('/')
			key = re.compile(k)
			if inspect.isclass(v):
				new_controllers_mapping.append((key, v()))
			else:
				new_controllers_mapping.append((key, v))
		self.settings["controllers"] = new_controllers_mapping






