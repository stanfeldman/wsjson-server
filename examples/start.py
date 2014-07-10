# -*- coding: utf-8 -*-
from os import path
from wsjson.server import WsJsonServer

options = {
	"application": {
		"address": "127.0.01",
		"port": 8888
	},
	"mapping": {
		"controller1": Controller1
	},
	"files": path.join(path.dirname(__file__), 'files'),
	"ssl": {
		"key": "server.key",
		"cert": "server.crt"
	}
}

if __name__ == '__main__':
	app = WsJsonServer(options)
	app.start()


