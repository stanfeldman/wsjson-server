# -*- coding: utf-8 -*-
import json
from geventwebsocket.exceptions import WebSocketError
from putils.patterns import Singleton
import re
import logging
logger = logging.getLogger(__name__)


class Router(Singleton):
	CONNECTED = "router_connected"
	DISCONNECTED = "router_disconnected"

	def __init__(self, server):
		self.controllers_mapping = server.settings["controllers"]
		self.sockets = []
		self.eventer = server.eventer

	def __call__(self, environ, start_response):
		if 'wsgi.websocket' in environ:
			socket = environ['wsgi.websocket']
			self.handle(socket)
			return None
		else:
			start_response('404 Not Found', [('Content-Type', 'application/json')])
			return ["{'error':'not found}"]

	def handle(self, socket):
		self.on_open(socket)
		while True:
			try:
				message = socket.receive()
				if not message:
					self.on_close(socket)
					break
				self.on_message(socket, message)
			except WebSocketError:
				self.on_close(socket)
				break
			except Exception, e:
				logger.error("handle error %s", str(e), exc_info=True)
				self.on_close(socket)
				break

	def on_message(self, socket, message):
		data = json.loads(message)
		data_url = data["url"]
		if data_url[len(data_url)-1] == '/':
			data_url = data_url.rstrip('/')
		url_and_method = data_url.rsplit('/', 1)
		url = url_and_method[0]
		method = url_and_method[1]
		for (match_url, controller) in self.controllers_mapping:
			mtch = match_url.match(url)
			if mtch:
				action = getattr(controller, method)
				for key, value in mtch.groupdict().iteritems():
					data[key] = value
				action(Sender(socket, data_url, self), data)
				break

	def on_open(self, socket):
		self.sockets.append(socket)
		logger.info("connected to %s", socket.origin)
		self.eventer.publish(Router.CONNECTED, Sender(socket, "/", self))

	def on_close(self, socket):
		self.sockets.remove(socket)
		logger.info("disconnected")
		self.eventer.publish(Router.DISCONNECTED, Sender(socket, "/", self))


class Sender(object):
	def __init__(self, socket, url, router):
		self.socket = socket
		self.url = url
		self.router = router

	def send(self, data):
		if self.socket is None:
			return
		data["url"] = self.url
		try:
			if self.socket:
				self.socket.send(json.dumps(data))
		except WebSocketError:
			pass

	def send_all(self, data):
		data["url"] = self.url
		json_data = json.dumps(data)
		for socket in self.router.sockets:
			try:
				if socket:
					socket.send(json_data)
			except WebSocketError:
				pass

	def send_others(self, data):
		data["url"] = self.url
		json_data = json.dumps(data)
		for socket in self.router.sockets:
			if socket and socket != self.socket:
				try:
					if socket:
						socket.send(json_data)
				except WebSocketError:
					pass
