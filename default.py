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
from lib import utils


#Set global addon information first
__addon_id__ = 'script.audio.rhapsody'
__addon_cfg__ = xbmcaddon.Addon(__addon_id__)
__addon_path__ = __addon_cfg__.getAddonInfo('path')
__addon_version__ = __addon_cfg__.getAddonInfo('version')


class Application():
	__vars = None

	def __init__(self):
		self.__vars = {}  #dict for app vars
		self.user_data = {} #object to store cached data

		self.genre_tree__ = []  #json data from rhapsody
		self.genre_dict__ = {}  #object to store cached data

		self.artist = {}  #object to store cached data                                convert to self-managing data class instance
		self.artist_file = __addon_path__+'/resources/.artistdb.obj'  #picklefile

		self.album = {}  #object to store cached data
		self.album_file = __addon_path__+'/resources/.albumdb.obj'  #picklefile

		self.genre = {}  #object to store cached data
		self.genre_file = __addon_path__+'/resources/.genres.obj'  #picklefile



	def set_var(self, name, value):
		self.__vars[name] = value


	def has_var(self, name):
		return name in self.__vars


	def get_var(self, name):
		return self.__vars[name]


	def remove_var(self, name):
		del self.__vars[name]

	def save_genre_data(self):
		self.genre['genretree'] = self.genre_tree__
		self.genre['genredict'] = self.genre_dict__
		self.genre['timestamp'] = time.time()
		jar = open(self.genre_file, 'wb')
		pickle.dump(self.genre, jar)
		jar.close()
		print "Genre data saved!"


	def save_album_data(self):
		jar = open(self.album_file, 'wb')
		pickle.dump(self.album, jar)
		jar.close()
		print "Album info saved in cachefile!"

	def save_artist_data(self):
		jar = open(self.artist_file, 'wb')
		pickle.dump(self.artist, jar)
		jar.close()
		print "Artist info saved in cachefile!"


	def load_cached_data(self):
		print "checking cached data"
		try:
			pkl_file = open(self.album_file, 'rb')
			self.album = pickle.load(pkl_file)
			pkl_file.close()
			print "Loaded Album cache"
		except:
			print "Couldn't read album cache file. Skipping..."

		try:
			pkl_file = open(self.artist_file, 'rb')
			self.artist = pickle.load(pkl_file)
			pkl_file.close()
			print "Loaded Artist cache"
		except:
			print "Couldn't read artist cache file. Skipping..."

		try:
			pkl_file = open(self.genre_file, 'rb')
			self.genre = pickle.load(pkl_file)
			pkl_file.close()
			self.genre_tree__ = self.genre['genretree']
			self.genre_dict__ = self.genre['genredict']
			print "Loaded Genre cache"
		except:
			print("Couldn't read genre cache file. Regenerating...")
			genres.get_genre_tree()
			genres.flatten_genre_keys(app.genre_tree__)
			self.save_genre_data()


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
		self.pos = None
		self.playing_pos = None
		self.current_playlist_albumId = None
		#self.browse_menu = ["browse_newreleases","browse_topalbums","browse_topartists","browse_toptracks"]
		#self.library_menu = ["library_albums", "library_artists", "library_tracks", "library_stations", "library_favorites"]
		#print "Script path: " + __addon_path__


	def onInit(self):

		self.win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
		self.win.setProperty("browseview", app.get_var('current_view'))
		self.win.setProperty("frame", app.get_var('current_frame'))
		self.alb_dialog = None
		self.main()

	def main(self):

		self.win.setProperty("full_name", mem.first_name+" "+mem.last_name)
		self.win.setProperty("country", mem.catalog)
		self.win.setProperty("logged_in", "true")
		self.clist = self.getControl(201)
		self.frame_label = self.getControl(121)
		self.draw_mainwin()


	def onAction(self, action):
		if action.getId() == 7:
			self.manage_action()
		if action.getId() == 10:
			self.goodbye()
		elif action.getId() == 92:
			self.goodbye()
		else:
			pass

	def goodbye(self):
		dialog = xbmcgui.Dialog()
		if dialog.yesno("Quit Rhapsody?", "Nobody like a quitter. Nobody. "):
			app.set_var('running',False)
			player.stop()
			playlist.clear()
			self.close()

	def manage_action(self):
		if self.getFocusId() == 201:
			if win.getProperty("frame") == "Browse":
				app.set_var('current_view', self.win.getProperty('browseview'))
			if win.getProperty("frame") == "Library":
				app.set_var('current_view', self.win.getProperty('browseview'))
			self.draw_mainwin()

		elif self.getFocusId() == 101:
			print "Clicked left nav menu: "+self.win.getProperty("frame")
			frame = self.win.getProperty("frame")
			if frame == "Search":
				pass
			elif frame == "Browse":
				app.set_var('current_view', "browse_newreleases")
				self.win.setProperty("browseview", app.get_var('current_view'))

			elif frame == "Radio":
				pass
			elif frame == "Library":
				app.set_var('current_view', "library_albums")
				self.win.setProperty("browseview", app.get_var('current_view'))

			elif frame == "Playlists":
				pass
			elif frame == "Listening History":
				pass
			elif frame == "Queue":
				pass
			elif frame == "Settings":
				pass
			self.draw_mainwin()

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
		self.pos = self.getCurrentListPosition()
		if control == 50:
			self.alb_dialog = AlbumDialog("album.xml", __addon_path__, 'Default', '720p', current_list=app.get_var(list),
			                         pos=self.pos)
			self.alb_dialog.setProperty("review", "has_review")
			self.alb_dialog.doModal()
			if self.empty_list():
				self.draw_mainwin()
			self.setCurrentListPosition(self.alb_dialog.pos)
			app.save_album_data()


	def onFocus(self, control):
		#print("onfocus(): control %i" % control)
		pass

	def draw_list(self, inst):
		app.set_var(list, inst.data)
		self.make_visible(300, 50)
		inst.make_active()
		self.setFocusId(50)
		if self.pos:
			self.setCurrentListPosition(self.pos)

	def make_visible(self, *args):
		for item in args:
			self.getControl(item).setVisible(True)

	def empty_list(self):
		if self.getListSize() < 2:
			return True


	def draw_mainwin(self):

		d = {"browse_newreleases": newreleases,
		     "browse_topalbums":   topalbums,
		     "browse_topartists":  topartists,
		     "browse_toptracks":   toptracks,
		     "library_albums":     lib_albums,
		     "library_artists":    lib_artists,
		     #"library_tracks":     lib_tracks,
		     #"library_stations":   lib_stations,
		     #"library_favorites":  lib_favorites
		     }

		v = app.get_var('current_view')

		self.draw_list(d[v])


	def sync_current_list_pos(self):
		try:
			if self.current_playlist_albumId == self.alb_dialog.current_list[self.alb_dialog.pos]["album_id"]:
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
		self.pos = kwargs.get('pos')
		self.img_dir = __addon_path__+'/resources/skins/Default/media/'


	def onInit(self):
		self.show_info()


	def show_info(self):
		self.reset_fields()
		self.clearList()
		self.getControl(11).setText(self.current_list[self.pos]["album"])
		self.getControl(13).setLabel(self.current_list[self.pos]["artist"])
		self.getControl(8).setLabel(self.current_list[self.pos]["album_date"])
		self.manage_artwork(self.current_list, self.pos)
		self.getControl(7).setImage(self.current_list[self.pos]["bigthumb"])
		self.manage_review(self.current_list, self.pos)
		self.getControl(14).setText(self.current_list[self.pos]["review"])
		self.manage_details(self.current_list, self.pos)
		self.getControl(10).setLabel(self.current_list[self.pos]["label"])
		self.getControl(6).setLabel(self.current_list[self.pos]["style"])
		self.manage_tracklist(self.current_list, self.pos)

	def manage_tracklist(self, list, pos):
		liz = tracklist.get_litems(app.album, list[pos]["album_id"])
		for item in liz:
			self.addItem(item)
		win.sync_current_list_pos()

	def onAction(self, action):
		if action.getId() == 7:                     # --- Enter / Select ---
			if self.getFocusId() == 21:             # --- Play Button ---
				self.start_playback(self.getFocusId())
			elif self.getFocusId() == 27:           # --- Next Button ---
				self.pos = (self.pos+1) % len(self.current_list)
				self.show_info()
			elif self.getFocusId() == 26:           # --- Prev Button ---
				self.pos = (self.pos-1) % len(self.current_list)
				self.show_info()
			elif self.getFocusId() == 51:           # --- Tracklist ---
				self.start_playback(self.getFocusId())
			else: pass
		elif action.getId() == 10:                  # --- Back ---
			self.close()
		elif action.getId() == 92:                  # --- Esc ---
			self.close()
		elif action.getId() == 18:                  # --- Tab ---
			self.close()
		else:
			pass


	def start_playback(self, id):
		if not self.now_playing_matches_album_dialog():
			player.now_playing = {'pos': 0, 'type':'album', 'item':self.current_list[self.pos]}
			playlist.build()
		if id == 51:
			player.now_playing['pos'] = self.getCurrentListPosition()
		xbmc.executebuiltin("XBMC.Notification(Rhapsody, Fetching song...)")
		track = playlist.add_playable_track(0)
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
			if player.now_playing['item']['album_id'] == self.current_list[self.pos]["album_id"]:
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


	def manage_review(self, list, pos):
		alb_id = list[pos]["album_id"]
		if not (app.album[alb_id]["review"] == ""):
			list[pos]["review"] = app.album[alb_id]["review"]
			print "Using review from cached album data"
			return
		elif list[pos]["review"] == "":
			print "Getting review from Rhapsody"
			review = api.get_album_review(alb_id)
			if not review:
				if list[pos]['artist_id'] == "Art.0":
					print "No review for Various Artists"
					return
				else:
					review = api.get_bio(list[pos]['artist_id'])
					print "No review. Trying artist bio for album review space"
				#print review
			if review:
				#print review
				list[pos]["review"] = review
				app.album[alb_id]["review"] = review
			else:
				print "No bio available for this artist either. :-("
				list[pos]["review"] = ""
				app.album[alb_id]['review'] = ""
		else:
			print "Already have the review in memory for this album"

	def manage_details(self, list, pos):
		alb_id = list[pos]["album_id"]
		if list[pos]["label"] == "":
			# try to get info from cached album data
			if app.album.has_key(alb_id) and (app.album[alb_id]['label'] != ""):
				print "Using genre, track, and label from cached album data"
				list[pos]["label"] = app.album[alb_id]["label"]
				list[pos]["tracks"] = app.album[alb_id]["tracks"]
				list[pos]["style"] = app.album[alb_id]["style"]
				#utils.prettyprint(list[pos]["tracks"])
			else:
				print "Getting genre, tracks and label from Rhapsody"
				results = api.get_album_details(alb_id)

				if results:
					list[pos]["label"] = results["label"]
					app.album[alb_id]['label'] = results['label']
					list[pos]["tracks"] = results["trackMetadatas"]
					app.album[alb_id]["tracks"] = results["trackMetadatas"]
					list[pos]["style"] = results["primaryStyle"]
					app.album[alb_id]["style"] = results["primaryStyle"]
					#print "Got label and original date for album"
				else:
					print "Album Detail api not returning response"
				#utils.prettyprint(list[pos]["tracks"])
		else:
			print "Using genre, track, and label from cached album data"

	def manage_artwork(self, list, pos):
		alb_id = list[pos]["album_id"]
		if os.path.isfile(app.album[alb_id]['bigthumb']):
			list[pos]["bigthumb"] = app.album[alb_id]['bigthumb']
		else:
			if not list[pos]['thumb_url']:
				file = img.handler(list[pos]['thumb_url'], 'large', 'album')
			else:
				file = img.base_path+self.big_image(list[pos]["album_id"])
			list[pos]["bigthumb"] = file
			app.album[alb_id]['bigthumb'] = file

	def big_image(self, album_id):
		url = img.identify_largest_image(album_id, "album")
		bigthumb = img.handler(url, 'large', 'album')
		return bigthumb


class ContentList():
	#handle new releases, top albums, artist discography, library album list, etc.
	def __init__(self, *args):
		self.data = []
		self.liz = []
		self.built = False
		self.pos = None
		self.timestamp = time.time()
		self.type = args[0]
		self.name = args[1]
		self.filename = args[2]
		self.raw = None

	def fresh(self):
		return True

	def make_active(self):
		if (app.get_var('last_rendered_list') == self.name) and win.getListSize()>2:
			print "Window already has that list in memory. Skipping list building"
			return
		print "ContentList: make active " +self.name
		print "current frame: "+app.get_var('current_frame')
		print "current view: "+app.get_var('current_view')
		print "Built: "+str(self.built)
		print "Fresh: "+str(self.fresh())
		if self.built and self.fresh():
			print "doing simple list building for mainwin"
			self.build_winlist()
		else:
			print "Doing full data fetch and list building for mainwin"
			self.build()
		app.set_var('last_rendered_list', self.name)
		#print app.get_var('last_rendered_list')


	def build(self):
		print "ContentList: build (full)"
		results = self.download_list()
		if results:
			self.ingest_list(results)
		else:
			print "Couldn't get info from rhapsody about "+self.name

	def save_raw_data(self, data):
		jar = open(self.filename, 'wb')
		pickle.dump(data, jar)
		jar.close()
		print self.name+" info saved in cachefile!"

	def download_list(self):
		print "Download_list. self.filename: "+self.filename
		try:
			pkl_file = open(self.filename, 'rb')
			self.raw = pickle.load(pkl_file)
			pkl_file.close()
			print "Loaded cache file"
			r = self.raw
		except:
			print "No list cache file to load. Let's download it"
			d = {'newreleases':   api.get_new_releases,
			     'topalbums':     api.get_top_albums,
			     'topartists':    api.get_top_artists,
			     'toptracks':     api.get_top_tracks,
			     'lib_albums':    api.get_library_albums,
			     'lib_artists':   api.get_library_artists,
			     #'lib_tracks':    api.get_library_artist_tracks,
			     #'lib_stations':  api.get_library_stations,
			     #'lib_favorites': api.get_library_favorites
			     }
			r = d[self.name]()
			self.save_raw_data(r)
		return r

	def ingest_list(self, results):

		print "Ingest list. Type: "+self.type
		win.clearList()
		__ = {}

		d = {'album': app.album,
			 'artist': app.artist,
		     'track':  __,
		     'station': __}

		cache = d[self.type]

		for i, item in enumerate(results):
			id = item['id']
			if self.type == 'album':
				infos = self.process_album(i, item)
			elif self.type == 'artist':
				infos = self.process_artist(i, item)
			elif self.type == 'track':
				infos = self.process_track(i, item)
			self.data.append(infos[self.type])
			self.liz.append(infos['listitem'])
			self.add_lizitem_to_winlist(infos['listitem'])
			if not id in cache:
				cache[id] = infos[self.type]

		self.built = True
		#app.save_album_data()

	def process_album(self, count, item):
		data = {}
		thumb = img.handler(item["images"][0]["url"], 'small', 'album')
		data['album'] = {'album_id': item["id"],
		         'album': item["name"],
		         'thumb': thumb,
		         'thumb_url': item["images"][0]["url"],
		         'album_date': time.strftime('%B %Y', time.localtime(int(item["released"]) / 1000)),
		         'orig_date': "",
		         'label': "",
		         'review': "",
		         'bigthumb': "",
		         'tracks': "",
		         'style': '',
		         'artist': item["artist"]["name"],
		         'list_id': count,
		         'artist_id': item["artist"]["id"]}
		data['listitem'] = xbmcgui.ListItem(item["name"], item["artist"]["name"], '', thumb)
		return data

	def process_artist(self, count, item):
		id = item['id']
		print "processing "+id
		data = {}

		if not id in app.artist:
			if id == 'Art.0':
				print "detected artist 0 case!"
				url = None
				genre = ""
			else:
				url = img.identify_largest_image(item["id"], "artist")
				g_id = api.get_artist_genre(item["id"])
				genre = app.genre_dict__[g_id]
		else:
			#print 'using cached thumb url for artist image'
			url = app.artist[id]['thumb_url']
			#print 'using cached genre for artist'
			genre = app.artist[id]['style']

		bigthumb = img.handler(url, 'large', 'artist')

		data['artist'] = {'artist_id': item["id"],
		         'name': item["name"],
		         'thumb': bigthumb,
		         'thumb_url': url,
		         'bio': "",
		         'bigthumb': bigthumb,
		         'toptracks': "",
		         'style': genre,
		         'list_id': count}
		data['listitem'] = xbmcgui.ListItem(item["name"], data["artist"]["style"], '', bigthumb)
		return data

	def process_track(self, count, item):
		data = {}
		#thumb = img.handler(item["images"][0]["url"], 'small', 'album')
		data['track'] = {'track_id': item["id"],
		         'track_name': item["name"],
		         #'thumb': thumb,
		         #'thumb_url': item["images"][0]["url"],
		         'album': item['album']['name'],
		         'album_id': item['album']['id'],
		         'genre_id': item['genre']['id'],
		         'duration': item['duration'],
		         'style': '',
		         'artist': item["artist"]["name"],
		         'artist_id': item["artist"]["id"],
		         'list_id': count}
		data['listitem'] = xbmcgui.ListItem(item["name"], item["artist"]["name"])
		info = {
	            "title": item["name"],
	            "album": item['album']['name'],
	            "artist": item["artist"]["name"],
	            "duration": item['duration'],
	            "tracknumber": count+1,
				}
		data['listitem'].setInfo("music", info)
		return data

	def add_lizitem_to_winlist(self, li):
		win.addItem(li)

	def build_winlist(self):
		print "ContentList: build_winlist"
		win.clearList()
		for i, item in enumerate(self.liz):
			win.addItem(self.liz[i])
			#xbmc.sleep(2)


class TrackList():
	def __init__(self):
		pass
	#handle albums, playlists, radio, queue, listening history

	def get_litems(self, cache, id):
		src = cache[id]
		#utils.prettyprint(src)
		x = 0
		list = []
		for item in src["tracks"]:
			newlistitem = xbmcgui.ListItem(path="http://dummyurl.org")
			newlistitem.setInfo('music', { 'tracknumber':   int(src["tracks"][x]["trackIndex"]),
			                               'title':         src["tracks"][x]["name"],
			                               'duration':      int(src["tracks"][x]["playbackSeconds"])
			                               })
			list.append(newlistitem)
			x += 1
		print "Album has "+str(x)+" tracks"
		return list



class ArtistList():
	def __init__(self):
		pass
	#handle top artists, artist library list, editorial artist lists, etc.


class Genres():
	def __init__(self):
		#self.get_genre_tree()
		#self.flatten_genre_keys(app.genre_tree__)
		#app.save_genre_data()
		pass


	def get_genre_tree(self):
		results = api.get_genres()
		if results:
			app.genre_tree__ = results
		else:
			print "Couldn't retrieve genres!"

	def flatten_genre_keys(self, j):
		for item in j:
			app.genre_dict__[item['id']] = item['name']
			#print "added a key for "+item['name']
			if 'subgenres' in item:
				#print "found subgenres. Calling self recursively"
				self.flatten_genre_keys(item['subgenres'])


class Player(xbmc.Player):

	def __init__(self):
		self.now_playing = {'pos': 0, 'type': None,'item':{}}
		self.now_playing['item']['album_id'] = 'blank'
		self.onplay_lock = False

	def onPlayBackStarted(self):
		if not player.onplay_lock:
			player.onplay_lock = True
			win.sync_current_list_pos()
			pos = playlist.getposition()
			self.now_playing['pos'] = pos
			print "Playing track "+str(pos+1)
			playlist.add_playable_track(1)
			playlist.add_playable_track(-1)
			win.sync_current_list_pos()
			pos2 = playlist.getposition()
			#print "pos: "+str(pos)+" pos2: "+str(pos2)
			if pos != pos2:
				print "Oh wait! We're not playing track "+str(pos+1)+"!"
				print "Playing track "+str(pos2+1)
				print "There, fixed it for ya. "
				self.now_playing['pos'] = pos2
				playlist.add_playable_track(1)
				playlist.add_playable_track(-1)
			xbmc.sleep(2)
			player.onplay_lock = False
		else:
			print "--------- blocked an extra play action from XBMC --------"


	def onPlayBackResumed(self):
		if not player.onplay_lock:
			player.onplay_lock = True
			win.sync_current_list_pos()
			pos = playlist.getposition()
			self.now_playing['pos'] = pos
			print "Playing track "+str(pos+1)
			playlist.add_playable_track(1)
			playlist.add_playable_track(-1)
			win.sync_current_list_pos()
			pos2 = playlist.getposition()
			#print "pos: "+str(pos)+" pos2: "+str(pos2)
			if pos != pos2:
				print "Oh wait! We're not playing track "+str(pos+1)+"!"
				print "Playing track "+str(pos2+1)
				print "There, fixed it for ya. "
				self.now_playing['pos'] = pos2
				playlist.add_playable_track(1)
				playlist.add_playable_track(-1)

			xbmc.sleep(2)
			player.onplay_lock = False
		else:
			print "--------- blocked an extra play action from XBMC --------"

	def onPlayBackEnded(self):
		print "onPlaybackEnded was detected!"

	def onPlayBackStopped(self):
		print "onPlaybackStopped was detected!"

	def onQueueNextItem(self):
		print "onQueueNextItem was detected!"

class PlayList(xbmc.PlayList):

	def build(self):
		playlist.clear()
		list = player.now_playing['item']['tracks']
		for i, track in enumerate(list):
			playlist.add(track['previewURL'], listitem=xbmcgui.ListItem(''))
		print "Okay let's play some music! Added "+str(i)+" tracks to the playlist for "+player.now_playing['item']["album_id"]
		xbmc.executebuiltin("XBMC.Notification(Rhapsody, Preparing to play...)")
		win.current_playlist_albumId = player.now_playing['item']["album_id"]  #can probably eliminate this variable


	def add_playable_track(self, offset):
		circ_pos = (player.now_playing['pos']+offset)%self.size()
		print "Fetching track "+str(circ_pos+1)
		tid = player.now_playing['item']['tracks'][circ_pos]['trackId']
		tname = self.__getitem__(circ_pos).getfilename()
		playurl = api.get_playable_url(tid)
		if not playurl:
			return False
		self.remove(tname)
		li = xbmcgui.ListItem(
	            player.now_playing['item']["tracks"][circ_pos]["name"],
	            path=player.now_playing['item']["tracks"][circ_pos]["previewURL"],
	            iconImage=img.base_path+player.now_playing['item']["thumb"],
	            thumbnailImage=img.base_path+player.now_playing['item']["thumb"]
				)
		info = {
	            "title": player.now_playing['item']["tracks"][circ_pos]["name"],
	            "album": player.now_playing['item']["album"],
	            "artist": player.now_playing['item']["artist"],
	            "duration": player.now_playing['item']["tracks"][circ_pos]["playbackSeconds"],
	            "tracknumber": int(player.now_playing['item']["tracks"][circ_pos]["trackIndex"]),
				}
		li.setInfo("music", info)
		self.add(playurl, listitem=li, index=circ_pos)
		return True



#gc.disable()

app = Application()
mem = member.Member()
mem.set_addon_path(__addon_path__)

genres = Genres()
player = Player()
playlist = PlayList(xbmc.PLAYLIST_MUSIC)
api = rhapapi.Api()
img = image.Image(__addon_path__)

newreleases =   ContentList('album',   'newreleases',   __addon_path__+'/resources/.newreleases.obj')
topalbums =     ContentList('album',   'topalbums',     __addon_path__+'/resources/.topalbums.obj')
topartists =    ContentList('artist',  'topartists',    __addon_path__+'/resources/.topartists.obj')
toptracks =     ContentList('track',   'toptracks',     __addon_path__+'/resources/.toptracks.obj')
lib_albums =    ContentList('album',   'lib_albums',    __addon_path__+'/resources/.lib_albums.obj')
lib_artists =   ContentList('artist',  'lib_artists',   __addon_path__+'/resources/.lib_artists.obj')
#lib_tracks =    ContentList('track',   'lib_tracks',    __addon_path__+'/resources/.lib_tracks.obj')
#lib_stations =  ContentList('station', 'lib_stations',  __addon_path__+'/resources/.lib_stations.obj')
#lib_favorites = ContentList('tracks',  'lib_favorites', __addon_path__+'/resources/.lib_favorites.obj')
tracklist = TrackList()

app.set_var('running', True)
app.set_var('logged_in', False)
app.set_var('bad_creds', False)
app.set_var('current_view', "browse_newreleases")
app.set_var('current_frame', "Browse")
app.set_var('last_rendered_list', None)

loadwin = xbmcgui.WindowXML("loading.xml", __addon_path__, 'Default', '720p')
loadwin.show()
loadwin.getControl(10).setLabel('Getting things ready...')
app.load_cached_data()
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
	win = MainWin("main.xml", __addon_path__, 'Default', '720p')
	win.doModal()
	if app.get_var('logged_in') == False:
		loadwin.getControl(10).setLabel('Logging you out...')
	else:
		loadwin.getControl(10).setLabel('Finishing up...')
	del win
	t1 = time.time()
	app.save_album_data()
	app.save_artist_data()
	t2 = time.time()
	print "Album data save operation took "+str(t2-t1)
	time.sleep(1)
	#print "Saved album data to cachefile"
del loadwin
gc.collect()
print "Rhapsody addon has exited"


