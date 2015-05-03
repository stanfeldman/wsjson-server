from distutils.core import setup
try:
	from setuptools import setup
except:
	pass

setup(
    name = "wsjson",
    version = "0.7",
    author = "Stanislav Feldman",
    description = ("Websocket server over Gevent wsgi server with json communication"),
    url = "https://github.com/stanislavfeldman/wsjson-server",
    keywords = "websocket gevent json",
    packages=[
    	"wsjson"
    ],
    install_requires = ["gevent", "gevent-websocket", "werkzeug", "putils", "pev"],
    classifiers=[],
)
