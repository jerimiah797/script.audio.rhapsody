import xbmc
import xbmcgui
import time
import sys
from lib import view
from lib import main
from lib import skincheck
from lib import utils
from lib import plugin
#from lib import bottle
#from lib import serve
#from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from lib.bottle import route, run, template, WSGIRefServer

import thread
import threading
from threading import Thread

REMOTE_DBG = False
TEST = True
PORT_NUMBER = 8090
global OFFLINE = True

# append pydev remote debugger
if REMOTE_DBG:
	# Make pydev debugger works for auto reload.
	# Note pydevd module need to be copied in XBMC\system\python\Lib\pysrc
	try:
		import pysrc.pydevd as pydevd
		# stdoutToServer and stderrToServer redirect stdout and stderr to eclipse console
		pydevd.settrace('localhost', stdoutToServer=True, stderrToServer=True)
	except ImportError:
		sys.stderr.write("Error: " + 
            "You must add org.python.pydev.debug.pysrc to your PYTHONPATH.")
		sys.exit(1)

print sys.argv




if len(sys.argv) < 2:
	skincheck.skinfix()   # verify fonts are installed
	utils.housekeeper()   #clean cached metadata files if necessary
	app = main.Application()
	#rhapserver = serve.RhapServer(app)
	#rhapserver.start("localhost", 8090)

	app.loadwin.getControl(10).setLabel('Welcome to Rhapsody')
	xbmc.sleep(2000)
	app.loadwin.getControl(10).setLabel('Checking Rhapsody servers...')
	results = app.api.get_artist_genre("Art.954")
	if results:
		print "Performing normal app startup"
		app.loadwin.getControl(10).setLabel('Loading fonts...')
		app.init_fonts()
		xbmc.sleep(1000)
		app.loadwin.getControl(10).setLabel('Getting things ready...')
		app.cache.load_cached_data()
		xbmc.sleep(1000)
	else:
		if TEST == True:
			print "*****************OFFLINE TEST MODE*****************"
			app.loadwin.getControl(10).setLabel('Starting in OFFLINE TEST mode...')
			xbmc.sleep(1000)
			app.cache.load_cached_data()
		else:
		 	app.loadwin.getControl(10).setLabel('Can\'t reach Rhapsody servers. \nExiting...')
		 	xbmc.sleep(2000)
		 	app.set_var('running', False)



	while app.get_var('running'):
		if not app.get_var('logged_in'):
			if not app.mem.has_saved_creds():
				logwin = view.LoginWin("login.xml", app.__addon_path__, 'Default', '720p', app=app)
				logwin.doModal()
				if not app.get_var('exiting'):
					app.loadwin.getControl(10).setLabel('Logging you in...')
					xbmc.sleep(1000)
				else:
					app.loadwin.getControl(10).setLabel('Finishing up...')
				del logwin
				xbmc.sleep(2000)
			else:
				app.loadwin.getControl(10).setLabel('Logging you in ...')
				app.set_var('logged_in', True)
				xbmc.sleep(1000)
			app.api.token = app.mem.access_token
		if not app.get_var('exiting'):
			app.win.doModal()
			if app.get_var('logged_in') == False:
				app.loadwin.getControl(10).setLabel('Logging you out...')
				app.reinit_lists()
			else:
				app.loadwin.getControl(10).setLabel('Finishing up...')
				app.cache.save_album_data()
				app.cache.save_artist_data()
				if app.cache.genre_modified == True:
					print "Saving updated genre data"
					app.cache.save_genre_data()
				xbmc.sleep(2000)
	if not app.get_var('exiting'):
		del app.win
	xbmc.sleep(1000)
	app.loadwin.close()
	del app.loadwin
	del app
	#rhapserver.server.shutdown()
	#del rhapserver
	print "Rhapsody addon has exited."
else:
	#print "Rhapsody plugin call invoked."
	plugin.get_it(sys.argv)
	




