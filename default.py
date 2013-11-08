import xbmcgui
import xbmc
import xbmcaddon
import pickle
import os
import gc
import time
from lib import rhapapi
from lib import image
from lib import member
from lib import play
from lib import view
from lib import lists
from lib import utils
from lib import caching


#Set global addon information first
__addon_id__ = 'script.audio.rhapsody'
__addon_cfg__ = xbmcaddon.Addon(__addon_id__)
__addon_path__ = __addon_cfg__.getAddonInfo('path')
__addon_version__ = __addon_cfg__.getAddonInfo('version')


class Application():
	__vars = None

	def __init__(self):
		self.__vars = {}  #dict for app vars
		self.view_keeper = {'browseview': 'browse_newreleases', 'frame': 'Browse'}


	def set_var(self, name, value):
		self.__vars[name] = value


	def has_var(self, name):
		return name in self.__vars


	def get_var(self, name):
		return self.__vars[name]


	def remove_var(self, name):
		del self.__vars[name]



class LoginWin(xbmcgui.WindowXML):
	def __init__(self, xmlName, thescriptPath, defaultname, forceFallback):
		pass


	def onInit(self):
		print "Starting onInit Loop"
		while not app.get_var('logged_in'):
			if app.get_var('bad_creds'):
				self.getControl(10).setLabel('Login failed! Try again...')
				print "Set fail label message"
			self.inputwin = InputDialog("input.xml", __addon_path__, 'Default', '720p')
			self.inputwin.doModal()
			data = mem.login_member(self.inputwin.name_txt, self.inputwin.pswd_txt)
			app.set_var('logged_in', data['logged_in'])
			app.set_var('bad_creds', data['bad_creds'])
			del self.inputwin
			print "Logged_in value: " + str(app.get_var('logged_in'))
			print "Bad Creds value: " + str(app.get_var('bad_creds'))

		print "Exited the while loop! Calling the del function"
		self.close()


class InputDialog(xbmcgui.WindowXMLDialog):

	def __init__(self, xmlFilename, scriptPath, defaultSkin, defaultRes):
		self.name = xbmcgui.ControlEdit(530, 320, 400, 120, '', 'rhapsody_font16', '0xDD171717', focusTexture="none.png")
		self.pswd = xbmcgui.ControlEdit(530, 320, 400, 120, '', font='rhapsody_font16', textColor='0xDD171717', focusTexture="none.png", isPassword=1)
		self.butn = None
		self.name_txt = ""
		self.pswd_txt = ""

	def onInit(self):
		self.name_select = self.getControl(10)
		#self.name_select.setVisible(False)
		self.pswd_select = self.getControl(11)
		self.pswd_select.setVisible(False)
		self.addControl(self.name)
		self.addControl(self.pswd)
		self.butn = self.getControl(22)
		self.name.setPosition(600, 320)
		self.name.setWidth(400)
		self.name.controlDown(self.pswd)
		self.pswd.setPosition(600, 410)
		self.pswd.setWidth(400)
		self.pswd.controlUp(self.name)
		self.pswd.controlDown(self.butn)
		self.butn.controlUp(self.pswd)
		self.setFocus(self.name)


	def onAction(self, action):
		#print str(action.getId())
		#print type(action)
		if action.getId() == 7:
			if self.getFocus() == self.name:
				self.setFocus(self.pswd)
			elif self.getFocus() == self.pswd:
				self.setFocus(self.butn)
			elif self.getFocusId() == 22:
				self.close()
				self.name_txt = self.name.getText()
				self.pswd_txt = self.pswd.getText()
			else: pass
		elif action.getId() == 18:
			if self.getFocus() == self.name:
				self.setFocus(self.pswd)
			elif self.getFocus() == self.pswd:
				self.setFocus(self.butn)
			elif self.getFocus() == self.butn:
				self.setFocus(self.name)
			else: pass
		else:
			pass

	def onFocus(self, control):
		if control == 3001:
			self.name_select.setVisible(True)
			self.pswd_select.setVisible(False)
		elif control == 3002:
			self.name_select.setVisible(False)
			self.pswd_select.setVisible(True)
		elif control == 22:
			self.name_select.setVisible(False)
			self.pswd_select.setVisible(False)
		else: pass


class MainWin(xbmcgui.WindowXML):

	def __init__(self, xmlName, thescriptPath, defaultname, forceFallback):
		self.setup = False
		print "running _init_ for mainwin"
		#self.win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
		#self.win.setProperty("browseview", 'browse_newreleases')
		#self.win.setProperty("frame", 'Browse')

		#self.pos = None
		#self.playing_pos = None
		#self.current_playlist_albumId = None
		#self.browse_menu = ["browse_newreleases","browse_topalbums","browse_topartists","browse_toptracks"]
		#self.library_menu = ["library_albums", "library_artists", "library_tracks", "library_stations", "library_favorites"]
		#print "Script path: " + __addon_path__


	def onInit(self):
		print "running onInit for mainwin"
		self.handle = xbmcgui.Window(xbmcgui.getCurrentWindowId())
		self.handle.setProperty("browseview", app.view_keeper['browseview'])
		self.handle.setProperty("frame", app.view_keeper['frame'])
		#self.alb_dialog = None
		self.main()

	def main(self):
		self.handle.setProperty("full_name", mem.first_name+" "+mem.last_name)
		self.handle.setProperty("country", mem.catalog)
		self.handle.setProperty("logged_in", "true")
		self.clist = self.getControl(201)
		self.frame_label = self.getControl(121)
		view.draw_mainwin(self, app)


	def onAction(self, action):
		if action.getId() == 7:
			self.manage_action()
		if action.getId() == 10:
			utils.goodbye(self, app, player)
		elif action.getId() == 92:
			utils.goodbye(self, app, player)
		else:
			pass


	def manage_action(self):
		if self.getFocusId() == 201:
			view.draw_mainwin(self, app)
			app.view_keeper = {'browseview': self.getProperty('browseview'), 'frame': self.getProperty('frame')}

		elif self.getFocusId() == 101:
			view.draw_mainwin(self, app)
			app.view_keeper = {'browseview': self.getProperty('browseview'), 'frame': self.getProperty('frame')}

		elif self.getFocusId() == 1001:
			app.set_var('logged_in', False)
			try:
				os.remove(mem.filename)
			except OSError, e:  ## if failed, report it back to the user ##
				print ("Error: %s - %s." % (e.filename,e.strerror))
			player.stop()
			playlist.clear()
			self.close()

	def onClick(self, control):
		pos = self.getCurrentListPosition()
		id = app.get_var(list)[pos]#["album_id"]
		print "mainwin onClick: id: "+str(id)
		if control == 50:
			self.alb_dialog = AlbumDialog("album.xml", __addon_path__, 'Default', '720p', current_list=app.get_var(list),
			                         pos=pos, cache=cache.album, alb_id=id)
			self.alb_dialog.setProperty("review", "has_review")
			self.alb_dialog.doModal()
			self.alb_dialog.id = None
			if self.empty_list():
				view.draw_mainwin(self, app)
			self.setCurrentListPosition(self.alb_dialog.pos)
			cache.save_album_data()

		elif control == 51:
			self.start_playback(control)


	def start_playback(self, id):

		player.now_playing = {'pos': 0, 'type':'playlist', 'item':toptracks.data, 'id':'toptracks'}  #['data']}
		player.build()
		if id == 51:
			player.now_playing['pos'] = self.getCurrentListPosition()
		xbmc.executebuiltin("XBMC.Notification(Rhapsody, Fetching song...)")
		track = player.add_playable_track(0)
		if not track:
			xbmc.executebuiltin("XBMC.Notification(Rhapsody, Problem with this song. Aborting...)")
			print "Unplayable track. Can't play this track"
			#player.stop()
			return False
		player.playselected(player.now_playing['pos'])
		xbmc.executebuiltin("XBMC.Notification(Rhapsody, Playback started)")
		if id == 21:
			self.setCurrentListPosition(playlist.getposition())
			self.setFocusId(51)


	def onFocus(self, control):
		#print("onfocus(): control %i" % control)
		pass


	def make_visible(self, *args):
		for item in args:
			self.getControl(item).setVisible(True)

	def empty_list(self):
		if self.getListSize() < 2:
			return True


	def sync_playlist_pos(self):
		try:
			if player.now_playing['id'] == 'toptracks':
				print "syncing playlist pos because player.now_playing id is 'toptracks'"
				self.setCurrentListPosition(playlist.getposition())
				toptracks.pos = playlist.getposition()
			elif player.now_playing['id'] == self.alb_dialog.id:
				print "syncing playlist pos because player.now_player id is current album id"
				self.alb_dialog.setCurrentListPosition(playlist.getposition())
		except:
			pass


class DialogBase(xbmcgui.WindowXMLDialog):
	def __init__(self, xmlName, thescriptPath, defaultname, forceFallback):
		#print "I'm the base dialog class"
		pass


class AlbumDialog(DialogBase):

	def __init__(self, *args, **kwargs):
		DialogBase.__init__(self, *args)
		self.current_list = kwargs.get('current_list')
		self.cache = kwargs.get('cache')
		self.id = kwargs.get('alb_id')
		self.pos = kwargs.get('pos')
		self.img_dir = __addon_path__+'/resources/skins/Default/media/'


	def onInit(self):
		self.show_info(self.id, self.cache)


	def show_info(self, alb_id, cache):
		print "AlbumDialog: album id = "+self.id
		album = cache[alb_id]
		self.reset_fields()
		self.clearList()
		self.getControl(11).setText(album["album"])
		self.getControl(13).setLabel(album["artist"])
		self.getControl(8).setLabel(album["album_date"])
		self.manage_artwork(cache, album)
		self.getControl(7).setImage(album["bigthumb"])
		self.manage_review(cache, album)
		self.getControl(14).setText(album["review"])
		self.manage_details(cache, album)
		self.getControl(10).setLabel(album["label"])
		self.getControl(6).setLabel(album["style"])
		self.manage_windowtracklist(cache, album)

	def show_next_album(self, offset):
		self.pos = (self.pos+offset) % len(self.current_list)
		self.id = self.current_list[self.pos]#['album_id']
		self.show_info(self.id, self.cache)
		print str(self.pos)
		print len(self.current_list)

	def manage_windowtracklist(self, cache, album):
		print "AlbumDialog: Manage tracklist for gui list"
		liz = windowtracklist.get_litems(cache, album["album_id"])
		for item in liz:
			self.addItem(item)
		win.sync_playlist_pos()

	def onAction(self, action):
		if action.getId() == 7:                     # --- Enter / Select ---
			if self.getFocusId() == 21:             # --- Play Button ---
				self.start_playback(self.getFocusId(), self.cache[self.id])
			elif self.getFocusId() == 27:           # --- Next Button ---
				self.show_next_album(1)
			elif self.getFocusId() == 26:           # --- Prev Button ---
				self.show_next_album(-1)
			elif self.getFocusId() == 51:           # --- Tracklist ---
				self.start_playback(self.getFocusId(), self.cache[self.id])
			else: pass
		elif action.getId() == 10:                  # --- Back ---
			self.close()
		elif action.getId() == 92:                  # --- Esc ---
			self.close()
		elif action.getId() == 18:                  # --- Tab ---
			self.close()
		else:
			pass


	def start_playback(self, id, album):
		print "Album dialog: start playback"
		#utils.prettyprint(album['tracks'])
		if not self.now_playing_matches_album_dialog():
			print "hit the first if. building playlist"
			player.now_playing = {'pos': 0, 'type':'album', 'item':album['tracks'], 'id':album['album_id']}
			player.build()
		if player.now_playing['type'] != 'album':
			print "hit the second if. building playlist"
			player.now_playing = {'pos': 0, 'type':'album', 'item':album['tracks'], 'id':album['album_id']}
			player.build()
		#print "Now playing item list follows!"
		#utils.prettyprint(player.now_playing['item'])
		if id == 51:
			player.now_playing['pos'] = self.getCurrentListPosition()
		xbmc.executebuiltin("XBMC.Notification(Rhapsody, Fetching song...)")
		track = player.add_playable_track(0)
		if not track:
			xbmc.executebuiltin("XBMC.Notification(Rhapsody, Problem with this song. Aborting...)")
			print "Unplayable track. Can't play this track"
			#player.stop()
			return False
		player.playselected(player.now_playing['pos'])
		xbmc.executebuiltin("XBMC.Notification(Rhapsody, Playback started)")
		if id == 21:
			self.setCurrentListPosition(playlist.getposition())
			self.setFocusId(51)


	def now_playing_matches_album_dialog(self):
		try:
			if player.now_playing['id'] == self.id:
				return True
			else:
				return False
		except:
			return True


	def reset_fields(self):
		self.getControl(6).setLabel("")
		self.getControl(7).setImage("")
		self.getControl(8).setLabel("")
		self.getControl(10).setLabel("")
		self.getControl(11).setText("")
		self.getControl(13).setLabel("")
		self.getControl(14).setText("")


	def manage_review(self, cache, album):
		alb_id = album["album_id"]
		if album["review"] == "":
			print "Getting review from Rhapsody"
			review = api.get_album_review(alb_id)
			if not review:
				if album['artist_id'] == "Art.0":
					print "No review for Various Artists"
					return
				else:
					review = api.get_bio(album['artist_id'])
					print "No review. Trying artist bio for album review space"
				#print review
			if review:
				#print review
				album["review"] = review
			else:
				print "No bio available for this artist either. :-("
				album["review"] = ""
		else:
			print "Already have the review in memory for this album"

	def manage_details(self, cache, album):
		alb_id = album["album_id"]
		if album["label"] == "":
			# try to get info from cached album data
			if cache.has_key(alb_id) and (cache[alb_id]['label'] != ""):
				print "Using genre, track, and label from cached album data"
			else:
				print "Getting genre, tracks and label from Rhapsody"
				results = api.get_album_details(alb_id)
				if results:
					album["label"] = results["label"]
					album["tracks"] = results["trackMetadatas"]
					album["style"] = results["primaryStyle"]
				else:
					print "Album Detail api not returning response"
		else:
			print "Using genre, track, and label from cached album data"

	def manage_artwork(self, cache, album):
		alb_id = album["album_id"]
		if os.path.isfile(cache[alb_id]['bigthumb']):
			return
		else:
			if not album['thumb_url']:
				file = img.handler(album['thumb_url'], 'large', 'album')
			else:
				file = img.base_path+self.big_image(album["album_id"])
			album["bigthumb"] = file
			#cache[alb_id]['bigthumb'] = file

	def big_image(self, album_id):
		url = img.identify_largest_image(album_id, "album")
		bigthumb = img.handler(url, 'large', 'album')
		return bigthumb


app = Application()
mem = member.Member()
mem.set_addon_path(__addon_path__)
win = MainWin("main.xml", __addon_path__, 'Default', '720p')
cache = caching.Cache(__addon_path__)
api = rhapapi.Api()
img = image.Image(__addon_path__)

player = play.Player(win=win, cache=cache, img=img, api=api)
playlist = player.playlist


newreleases =   lists.ContentList('album',   'newreleases',   __addon_path__+'/resources/.newreleases.obj', app, win, cache, img, api)
topalbums =     lists.ContentList('album',   'topalbums',     __addon_path__+'/resources/.topalbums.obj', app, win, cache, img, api)
topartists =    lists.ContentList('artist',  'topartists',    __addon_path__+'/resources/.topartists.obj', app, win, cache, img, api)
toptracks =     lists.ContentList('track',   'toptracks',     __addon_path__+'/resources/.toptracks.obj', app, win, cache, img, api)
lib_albums =    lists.ContentList('album',   'lib_albums',    __addon_path__+'/resources/.lib_albums.obj', app, win, cache, img, api)
lib_artists =   lists.ContentList('artist',  'lib_artists',   __addon_path__+'/resources/.lib_artists.obj', app, win, cache, img, api)
#lib_tracks =    ContentList('track',   'lib_tracks',    __addon_path__+'/resources/.lib_tracks.obj')
#lib_stations =  ContentList('station', 'lib_stations',  __addon_path__+'/resources/.lib_stations.obj')
#lib_favorites = ContentList('tracks',  'lib_favorites', __addon_path__+'/resources/.lib_favorites.obj')
windowtracklist = lists.WindowTrackList()

app.set_var('view_matrix' , {"browse_newreleases": newreleases,
			                "browse_topalbums":   topalbums,
			                "browse_topartists":  topartists,
			                "browse_toptracks":   toptracks,
			                "library_albums":     lib_albums,
			                "library_artists":    lib_artists,
			                #"library_tracks":     lib_tracks,
			                #"library_stations":   lib_stations,
			                #"library_favorites":  lib_favorites
			                })

app.set_var('running', True)
app.set_var('logged_in', False)
app.set_var('bad_creds', False)
app.set_var('last_rendered_list', None)

loadwin = xbmcgui.WindowXML("loading.xml", __addon_path__, 'Default', '720p')
loadwin.show()
loadwin.getControl(10).setLabel('Getting things ready...')
cache.load_cached_data()
time.sleep(1)


while app.get_var('running'):
	if not app.get_var('logged_in'):
		if not mem.has_saved_creds():
			logwin = LoginWin("login.xml", __addon_path__, 'Default', '720p')
			logwin.doModal()
			loadwin.getControl(10).setLabel('Logging you in...')
			del logwin
			time.sleep(1)
		else:
			loadwin.getControl(10).setLabel('Logging you in...')
			app.set_var('logged_in', True)
			time.sleep(1)
		api.token = mem.access_token
	#win = MainWin("main.xml", __addon_path__, 'Default', '720p')
	win.doModal()
	if app.get_var('logged_in') == False:
		loadwin.getControl(10).setLabel('Logging you out...')
	else:
		loadwin.getControl(10).setLabel('Finishing up...')
	del win
	t1 = time.time()
	cache.save_album_data()
	cache.save_artist_data()
	t2 = time.time()
	print "Album data save operation took "+str(t2-t1)
	time.sleep(1)
	#print "Saved album data to cachefile"
del loadwin
gc.collect()
print "Rhapsody addon has exited"


