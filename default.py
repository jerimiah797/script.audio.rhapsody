import xbmcgui
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
	time.sleep(1)
loadwin.close()
del loadwin
del app
print "Rhapsody addon has exited"


