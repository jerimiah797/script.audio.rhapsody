# from wsgiref.simple_server import make_server

# # Every WSGI application must have an application object - a callable
# # object that accepts two arguments. For that purpose, we're going to
# # use a function (note that you're not limited to a function, you can
# # use a class for example). The first argument passed to the function
# # is a dictionary containing CGI-style envrironment variables and the
# # second variable is the callable object (see PEP 333).
# def hello_world_app(environ, start_response):
# 	status = '200 OK' # HTTP Status
# 	headers = [('Content-type', 'text/plain')] # HTTP Headers
# 	start_response(status, headers)

# 	# The returned object is going to be printed
# 	return ["Hello World"]

# httpd = make_server('', 8000, hello_world_app)
# print "Serving on port 8000..."

# # Serve until process is killed
# httpd.serve_forever()

import threading
import thread
from cgi import parse_qs
from wsgiref.simple_server import make_server





class TinyWebServer(object):
	def __init__(self, app):
		self.app = app

	def simple_app(self, environ, start_response):
	    status = '200 OK'
	    headers = [('Content-Type', 'text/plain')]
	    start_response(status, headers)
	    if environ['REQUEST_METHOD'] == 'POST':
	        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
	        request_body = environ['wsgi.input'].read(request_body_size)
	        d = parse_qs(request_body)  # turns the qs to a dict
	        return 'From POST: %s' % ''.join('%s: %s' % (k, v) for k, v in d.iteritems())
	    else:  # GET
	        d = parse_qs(environ['QUERY_STRING'])  # turns the qs to a dict
	        #return 'From GET: %s' % ''.join('%s: %s' % (k, v) for k, v in d.iteritems())
	        return "Token value: "+self.app.mem.access_token

	def create(self, ip_addr, port):
		self.httpd = make_server(ip_addr, port, self.simple_app)

	def start(self):
		"""
		start the web server on a new thread
		"""
		self._webserver_died = threading.Event()
		self._webserver_thread = threading.Thread(
				target=self._run_webserver_thread)
		self._webserver_thread.start()

	def _run_webserver_thread(self):
		self.httpd.serve_forever()
		self._webserver_died.set()

	def stop(self):
		if not self._webserver_thread:
			return

		thread.start_new_thread(self.httpd.shutdown, () )
		#self.httpd.server_close()

		# wait for thread to die for a bit, then give up raising an exception.
		#if not self._webserver_died.wait(5):
			#raise ValueError("couldn't kill webserver")
		print "Shutting down internal webserver"



