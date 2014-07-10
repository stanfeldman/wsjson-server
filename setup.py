from distutils.core import setup
try:
	from setuptools import setup
except:
	pass

setup(
    name = "wsjson",
    version = "0.1",
    author = "Stanislav Feldman",
    description = ("Websocket server over Gevent wsgi server with json communication"),
    url = "https://github.com/stanislavfeldman/wsjson-server",
    keywords = "websocket gevent json",
    packages=[
    	"wsjson"
    ],
    install_requires = ["gevent"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Application Frameworks"
    ],
)
