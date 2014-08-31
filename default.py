import xbmc
import xbmcgui
import time
import sys
from lib import view
from lib import main
from lib import skincheck
from lib import utils
from lib import plugin

REMOTE_DBG = False

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
	# verify fonts are installed
	skincheck.skinfix()

	app = main.Application()

	#loadwin = xbmcgui.WindowXML("loading.xml", app.__addon_path__, 'Default', '720p')
	#loadwin.show()
	# network check
	app.loadwin.getControl(10).setLabel('Checking Rhapsody servers...')
	if app.api.get_artist_genre("Art.954"):
		app.loadwin.getControl(10).setLabel('Installing fonts...')
		app.init_fonts()
		app.loadwin.getControl(10).setLabel('Getting things ready...')
		app.cache.load_cached_data()
		time.sleep(1)
	else:
		app.loadwin.getControl(10).setLabel('Can\'t reach Rhapsody servers. \nMust be online to use Rhapsody.\nExiting...')
		time.sleep(2)
		app.set_var('running', False)


	while app.get_var('running'):
		if not app.get_var('logged_in'):
			if not app.mem.has_saved_creds():
				logwin = view.LoginWin("login.xml", app.__addon_path__, 'Default', '720p', app=app)
				logwin.doModal()
				if not app.get_var('exiting'):
					app.loadwin.getControl(10).setLabel('Logging you in...')
				else:
					app.loadwin.getControl(10).setLabel('Finishing up...')
				del logwin
				time.sleep(1)
			else:
				app.loadwin.getControl(10).setLabel('Logging you in ...')
				app.set_var('logged_in', True)
				time.sleep(1)
			app.api.token = app.mem.access_token
			#utils.prettyprint(app.api.get_account_info())
			if app.get_var("logged_in"):
				app.mem.get_member_details()
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
	if not app.get_var('exiting'):
		del app.win
	time.sleep(1)
	app.loadwin.close()
	del app.loadwin
	del app
	print "Rhapsody addon has exited."
	#return
else:
	print "Rhapsody plugin call invoked."
	plugin.get_it(sys.argv)
	




