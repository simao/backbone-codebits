#!/home1/simaomat/python2.7/bin/python2.7

import server
import bottle

from flup.server.fcgi import WSGIServer
WSGIServer(bottle.default_app()).run()
