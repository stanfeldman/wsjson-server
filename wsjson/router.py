# -*- coding: utf-8 -*-
import json
from geventwebsocket.exceptions import WebSocketError
from putils.patterns import Singleton
import logging
logger = logging.getLogger(__name__)


class Router(Singleton):
	def __init__(self, controllers_mapping):
		self.controllers_mapping = controllers_mapping

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
			if match_url == url:
				action = getattr(controller, method)
				action(Sender(socket, data_url), data)
				break

	def on_open(self, socket):
		logger.info("connected to %s", socket.origin)

	def on_close(self, socket):
		logger.info("disconnected from %s", socket.origin)


class Sender(object):
	def __init__(self, socket, url):
		self.socket = socket
		self.url = url

	def send(self, data):
		data["url"] = self.url
		self.socket.send(json.dumps(data))

	def send_all(self, data):
		data["url"] = self.url
		for client in self.socket.handler.server.clients.values():
			client.ws.send(json.dumps(data))

	def socket_send_others(self, data):
		data["url"] = self.url
		for client in self.socket.handler.server.clients.values():
			if client.ws != self.socket:
				client.ws.send(json.dumps(data))
