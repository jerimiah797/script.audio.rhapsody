#from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer

#PORT_NUMBER = 8090   set port number in default.py

#This class will handles any incoming request from
#the browser 
#class myHandler(BaseHTTPRequestHandler):
	
	#Handler for the GET requests
#	def do_GET(self):
#		self.send_response(200)
#		self.send_header('Content-type','text/html')
#		self.end_headers()
		# Send the html message
#		self.wfile.write("Hello World !")
#		return

# try:
# 	#Create a web server and define the handler to manage the
# 	#incoming request
# 	server = HTTPServer(('', PORT_NUMBER), myHandler)
# 	print 'Started httpserver on port ' , PORT_NUMBER
	
# 	#Wait forever for incoming htto requests
# 	server.serve_forever()

# except KeyboardInterrupt:
# 	print '^C received, shutting down the web server'
# 	server.socket.close()



from lib.bottle import route, run, template, WSGIRefServer

import thread
import threading
from threading import Thread

class RhapServer():
	def __init__(self, app):
		self.server = None
		self.app = app

	@route('/hello/:name')
	def index(name='World'):
		return template('<b>Hello {{name}}</b>!', name=name)



	class MyServer(WSGIRefServer):
		def run(self, app): # pragma: no cover
			from wsgiref.simple_server import WSGIRequestHandler, WSGIServer
			from wsgiref.simple_server import make_server
			import socket

			class FixedHandler(WSGIRequestHandler):
				def address_string(self): # Prevent reverse DNS lookups please.
					return self.client_address[0]
				def log_request(*args, **kw):
					if not self.quiet:
						return WSGIRequestHandler.log_request(*args, **kw)

			handler_cls = self.options.get('handler_class', FixedHandler)
			server_cls  = self.options.get('server_class', WSGIServer)

			if ':' in self.host: # Fix wsgiref for IPv6 addresses.
				if getattr(server_cls, 'address_family') == socket.AF_INET:
					class server_cls(server_cls):
						address_family = socket.AF_INET6

			srv = make_server(self.host, self.port, app, server_cls, handler_cls)
			self.srv = srv ### THIS IS THE ONLY CHANGE TO THE ORIGINAL CLASS METHOD!
			srv.serve_forever()

		def shutdown(self): ### ADD SHUTDOWN METHOD.
			print "Shutting down server"
			self.srv.shutdown()
			self.srv.server_close()
			print "Done shutting down!"

	def begin(self):
		run(server=self.server)

	def start(self, host, port):
		self.server = self.MyServer(host="localhost", port=8090)
		Thread(target=self.begin).start()

	def stop(self):
		#thread.start_new_thread(self.server.shutdown, () )
		self.server.shutdown()





