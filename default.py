import xbmc
import xbmcgui
import time
import sys
from lib import view
from lib import main
from lib import skincheck
from lib import utils

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


skincheck.skinfix()

app = main.Application()

loadwin = xbmcgui.WindowXML("loading.xml", app.__addon_path__, 'Default', '720p')
loadwin.show()
print "Do we have network?"#+str(app.api.get_new_releases())
if app.api.get_new_releases():
	loadwin.getControl(10).setLabel('Installing fonts...')
	app.init_fonts()
	loadwin.getControl(10).setLabel('Getting things ready...')
	app.cache.load_cached_data()
	time.sleep(1)
else:
	loadwin.getControl(10).setLabel('Can\'t reach Rhapsody servers. \nMust be online to use Rhapsody.\nExiting...')
	time.sleep(2)
	app.set_var('running', False)


while app.get_var('running'):
	if not app.get_var('logged_in'):
		if not app.mem.has_saved_creds():
			logwin = view.LoginWin("login.xml", app.__addon_path__, 'Default', '720p', app=app)
			logwin.doModal()
			loadwin.getControl(10).setLabel('Logging you in...')
			del logwin
			time.sleep(1)
		else:
			loadwin.getControl(10).setLabel('Logging you in...')
			app.set_var('logged_in', True)
			time.sleep(1)
		app.api.token = app.mem.access_token
		#app.player.get_session()
		#app.player.validate_session(app.player.session)
	app.win.doModal()
	if app.get_var('logged_in') == False:
		loadwin.getControl(10).setLabel('Logging you out...')
	else:
		loadwin.getControl(10).setLabel('Finishing up...')
	app.cache.save_album_data()
	app.cache.save_artist_data()
	#utils.update()
del app.win
time.sleep(1)
loadwin.close()
del loadwin
del app
print "Rhapsody addon has exited"


