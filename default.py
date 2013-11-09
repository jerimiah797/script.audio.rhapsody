import xbmcgui
import gc
import time
from lib import view
from lib import main


app = main.Application()

loadwin = xbmcgui.WindowXML("loading.xml", app.__addon_path__, 'Default', '720p')
loadwin.show()
loadwin.getControl(10).setLabel('Getting things ready...')
app.cache.load_cached_data()
time.sleep(1)


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
	app.win.doModal()
	if app.get_var('logged_in') == False:
		loadwin.getControl(10).setLabel('Logging you out...')
	else:
		loadwin.getControl(10).setLabel('Finishing up...')
	del app.win
	t1 = time.time()
	app.cache.save_album_data()
	app.cache.save_artist_data()
	t2 = time.time()
	print "Album and artist data save operation took "+str(t2-t1)
	time.sleep(1)
del loadwin
gc.collect()
print "Rhapsody addon has exited"


