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
		self.browse_list = ["Browse_newreleases","Browse_topalbums","Browse_topartists","Browse_toptracks"]
		#print "Script path: " + __addon_path__


	def onInit(self):
		self.clist = self.getControl(201)
		self.clist.addItem('New Releases')
		self.clist.addItem('Top Albums')
		self.clist.addItem('Top Artists')
		self.clist.addItem('Top Tracks')
		self.win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
		self.win.setProperty("browseview", app.get_var('view'))
		self.win.setProperty("view", "Browse")
		#print "onInit(): Window initialized"
		#print "Starting the engines"
		self.main()

	def main(self):
		#print "self.win view property is "+self.win.getProperty("view")
		# set window properties
		self.win.setProperty("username", mem.username)
		self.win.setProperty("password", mem.password)
		self.win.setProperty("guid", mem.guid)
		self.win.setProperty("token", mem.access_token)
		#self.win.setProperty("account_type", mem.account_type)
		#self.win.setProperty("date_created", mem.date_created)
		self.win.setProperty("full_name", mem.first_name+" "+mem.last_name)
		self.win.setProperty("country", mem.catalog)
		self.win.setProperty("logged_in", "true")
		self.alb_dialog = None
		self.draw_mainwin_browse()


	def onAction(self, action):
		#print str(action.getId())
		#print type(action)
		if action.getId() == 7:
			if self.getFocusId() == 201:
				#print "onAction(): Clicked a menu item!"
				#print "onAction(): Item: " + str(self.getFocus(201).getSelectedPosition())
				menuitem = self.getFocus(201).getSelectedPosition()
				app.set_var('view', self.browse_list[menuitem])
				self.win.setProperty("browseview", app.get_var('view'))
				self.main()
			if self.getFocusId() == 1001:
				app.set_var('logged_in', False)
				try:
					os.remove(mem.filename)
				except OSError, e:  ## if failed, report it back to the user ##
					print ("Error: %s - %s." % (e.filename,e.strerror))
				player.stop()
				playlist.clear()
				self.close()
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


	def onClick(self, control):
		#print "onclick(): control %i" % control
		self.pos = self.getCurrentListPosition()
		if control == 50:
			#print "Opening album detail dialog"
			#print str(app.get_var(list))
			self.alb_dialog = AlbumDialog("album.xml", __addon_path__, 'Default', '720p', current_list=app.get_var(list),
			                         pos=self.pos)
			self.alb_dialog.setProperty("review", "has_review")
			self.alb_dialog.doModal()
			self.draw_mainwin_browse()
			self.setCurrentListPosition(self.alb_dialog.pos)
			del self.alb_dialog
			app.save_album_data()
		#if control == 201:
		#	print "I see you've clicked the nav menu"

	def onFocus(self, control):
		#print("onfocus(): control %i" % control)
		pass

	def draw_newreleases(self):
		app.set_var(list, newreleases.data)
		#self.getControl(300).setVisible(True)
		#self.getControl(50).setVisible(True)
		self.make_visible(300, 50)
		newreleases.make_active()

	def draw_topalbums(self):
		app.set_var(list, topalbums.data)
		#self.getControl(300).setVisible(True)
		#self.getControl(50).setVisible(True)
		self.make_visible(300, 50)
		topalbums.make_active()

	def make_visible(self, *args):
		print args
		for item in args:
			self.getControl(item).setVisible(True)

	def draw_mainwin_browse(self):
		if app.get_var('view') == "Browse_newreleases":
			print "draw mainwin with new releases"
			#app.save_album_data()
			self.draw_newreleases()
			self.setFocusId(50)
			if self.pos:
				self.setCurrentListPosition(self.pos)
		if app.get_var('view') == "Browse_topalbums":
			print "draw mainwin with top albums"
			#app.save_album_data()
			self.draw_topalbums()
			self.setFocusId(50)
			if self.pos:
				self.setCurrentListPosition(self.pos)

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
		playlist.add_playable_track(0)
		player.playselected(player.now_playing['pos'])
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
		self.getControl(7).setImage("none.png")
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
			if review:
				list[pos]["review"] = review
				app.album[alb_id]["review"] = review
			else:
				print "No review available for this album"
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
			file = img.base_path+self.big_image(list[pos]["album_id"])
			list[pos]["bigthumb"] = file
			app.album[alb_id]['bigthumb'] = file

	def big_image(self, album_id):
		url = img.identify_largest_image(album_id)
		bigthumb = img.handler(url, 'large', 'album')
		return bigthumb


class AlbumList():
	#handle new releases, top albums, artist discography, library album list, etc.
	def __init__(self, *args):
		self.data = []
		self.liz = []
		self.built = False
		self.pos = None
		self.timestamp = time.time()
		self.name = args[0]

	def fresh(self):
		return True

	def make_active(self):
		print "Built: "+str(self.built)
		print "Fresh: "+str(self.fresh())
		if self.built and self.fresh():
			print "doing simple list building for mainwin"
			self.build_winlist()
		else:
			print "Doing full data fetch and list building for mainwin"
			self.build()


	def build(self):
		results = self.download_list()
		if results:
			self.ingest_list(results)
		else:
			print "Couldn't get info from rhapsody about "+self.name

	def download_list(self):
		if self.name == 'newreleases':
			return api.get_new_releases()
		elif self.name == 'topalbums':
			return api.get_top_albums()

	def ingest_list(self, results):
		win.clearList()
		count = 0
		if results:
			for item in results:
				infos = self.process_album(count, item)
				self.data.append(infos['album'])
				self.liz.append(infos['listitem'])
				self.add_lizitem_to_winlist(infos['listitem'])
				if not app.album.has_key(item["id"]):
					app.album[item["id"]] = infos['album']
				count += 1
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

	def add_lizitem_to_winlist(self, li):
		win.addItem(li)

	def build_winlist(self):
		win.clearList()
		for x in range (0, len(self.liz)):
			win.addItem(self.liz[x])
			xbmc.sleep(2)


class TrackList():
	def __init__(self):
		pass
	#handle albums, playlists, radio, queue, listening history

	def get_litems(self, cache, id):
		src = cache[id]
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
		x = 0
		for track in player.now_playing['item']['tracks']:
			playlist.add(track['previewURL'], listitem=xbmcgui.ListItem(''))
			x += 1
		print "Okay let's play some music! Added "+str(x)+" tracks to the playlist for "+player.now_playing['item']["album_id"]
		#xbmc.executebuiltin("XBMC.Notification("+ __scriptname__ +",Event Has been triggered,60)")
		#xbmc.executebuiltin("XBMC.Notification(Added tracks to playlist for ya, Thank me later)")
		win.current_playlist_albumId = player.now_playing['item']["album_id"]  #can probably eliminate this variable


	def add_playable_track(self, offset):
		circ_pos = (player.now_playing['pos']+offset)%self.size()
		print "Fetching track "+str(circ_pos+1)
		tid = player.now_playing['item']['tracks'][circ_pos]['trackId']
		tname = self.__getitem__(circ_pos).getfilename()
		playurl = api.get_playable_url(tid, mem.access_token)
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






app = Application()
mem = member.Member()
mem.set_addon_path(__addon_path__)

genres = Genres()
player = Player()
playlist = PlayList(xbmc.PLAYLIST_MUSIC)
api = rhapapi.Api()
img = image.Image(__addon_path__)

newreleases = AlbumList('newreleases')
topalbums = AlbumList('topalbums')
tracklist = TrackList()

app.set_var('running', True)
app.set_var('logged_in', False)
app.set_var('bad_creds', False)
app.set_var('view', "Browse_newreleases")

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
	win = MainWin("main.xml", __addon_path__, 'Default', '720p')
	win.doModal()
	if app.get_var('logged_in') == False:
		loadwin.getControl(10).setLabel('Logging you out...')
	else:
		loadwin.getControl(10).setLabel('Finishing up...')
	del win
	t1 = time.time()
	app.save_album_data()
	t2 = time.time()
	print "Album data save operation took "+str(t2-t1)
	time.sleep(1)
	#print "Saved album data to cachefile"
del loadwin
gc.collect()
print "Rhapsody addon has exited"


