# -*- coding: utf-8 -*-
import json
from geventwebsocket.exceptions import WebSocketError
from putils.patterns import Singleton
import logging

logger = logging.getLogger(__name__)

class WsJsonRouter(Singleton):
	def __init__(self, mapping):
		self.mapping = mapping

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
		for (match_url, controller) in self.mapping:
			if match_url == url:
				action = getattr(controller, method)
				result = action(socket, data)
				result["url"] = data_url
				response = json.dumps(result)
				socket.send(response)
				logger.info("returned %s to %s%s", response, socket.origin.rstrip('/'), data_url)
				break

	def on_open(self, socket):
		logger.debug("connected to %s", socket.origin)

	def on_close(self, socket):
		logger.debug("disconnected from %s", socket.origin)