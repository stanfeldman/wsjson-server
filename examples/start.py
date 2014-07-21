# -*- coding: utf-8 -*-
from os import path
from wsjson.server import Server

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
	app = Server(options)
	app.start()


