import xbmcgui
import xbmc
import xbmcaddon
import xbmcplugin
import time
import urllib
import urllib2
import json
import pickle
import base64
import os
import gc



#Set global addon information first
__addon_id__ = 'script.audio.rhapsody'
addon_cfg = xbmcaddon.Addon(__addon_id__)
__addon_path__ = addon_cfg.getAddonInfo('path')
__addon_version__ = addon_cfg.getAddonInfo('version')


#__newreleases__ = []
__toptracks__ = []
#__topalbums__ = []
__topartists__ = []



class Application():
	__vars = None

	def __init__(self):
		self.__vars = {}
		self.user_data = {}

		self.newreleases__ = []
		self.newreleases_listitems = []
		self.newreleases = {}
		self.newreleases_file = __addon_path__+'/resources/.newreleases.obj'

		self.toptracks__ = []
		self.toptracks_listitems = []

		self.topalbums__ = []
		self.topalbums_listitems = []
		self.topalbums = {}
		self.topalbums_file = __addon_path__+'/resources/.topalbums.obj'

		self.topartists__ = []
		self.topartists_listitems = []

		self.genre_tree__ = []
		self.genre_dict__ = {}

		self.artist = {}

		self.album = {}
		self.album_file = __addon_path__+'/resources/.albumdb.obj'

		self.genre = {}
		self.genre_file = __addon_path__+'/resources/.genres.obj'


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
		pickle.dump(self.genre, open(self.genre_file, 'wb'))
		print "Genre data saved!"

	def save_newreleases_data(self):
		self.newreleases['newreleases'] = self.newreleases__
		self.newreleases['timestamp'] = time.time()
		pickle.dump(self.newreleases, open(self.newreleases_file, 'wb'))
		print "New Releases data saved!"

	def save_topalbums_data(self):
		self.topalbums['topalbums'] = self.topalbums__
		self.topalbums['timestamp'] = time.time()
		pickle.dump(self.topalbums, open(self.topalbums_file, 'wb'))
		print "Top Albums data saved!"

	def save_album_data(self):
		pickle.dump(self.album, open(self.album_file, 'wb'))
		print "Album info saved in cachefile!"

	def load_cached_data(self):
		print "checking cached data"
		try:
			self.album = pickle.load(open(self.album_file, 'rb'))
			print "Loaded Album cache"
		except:
			print "Couldn't read album cache file. Skipping..."

		try:
			self.genre = pickle.load(open(self.genre_file, 'rb'))
			self.genre_tree__ = self.genre['genretree']
			self.genre_dict__ = self.genre['genredict']
			print "Loaded Genre cache"
		except:
			print("Couldn't read genre cache file. Regenerating...")
			genres.get_genre_tree()
			genres.flatten_genre_keys(app.genre_tree__)
			self.save_genre_data()

		try:
			self.newreleases = pickle.load(open(self.newreleases_file, 'rb'))
			self.newreleases__ = self.newreleases['newreleases']
			print "Loaded New Releases cache"
		except:
			print "Couldn't read new releases cache file. Skipping..."

		try:
			self.topalbums = pickle.load(open(self.topalbums_file, 'rb'))
			self.topalbums__ = self.topalbums['topalbums']
			print "Loaded Top Albums cache"
		except:
			print "Couldn't read top albums cache file. Skipping..."

		#print "current time: "+str(time.time())
		#print "creds time: "+str(self.timestamp)
		#if time.time() - self.timestamp < self.expires_in:
		#	print "Saved creds look good. Automatic login successful!"
		#	app.set_var('logged_in', True)
		#	return True
		#else:
		#	print "Saved creds have expired. Generating new ones."
		#	self.login_member(self.username, self.password)





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
			mem.login_member(self.inputwin.name_txt, self.inputwin.pswd_txt)
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
		print str(action.getId())
		print type(action)
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
		self.pos = ""
		self.view = ""
		self.current_playlist_albumId = None
		#self.mem = Member()

		self.browse_list = ["Browse_newreleases","Browse_topalbums","Browse_topartists","Browse_toptracks"]
		print "Script path: " + __addon_path__


	def onInit(self):
		self.clist = self.getControl(201)
		self.clist.addItem('New Releases')
		self.clist.addItem('Top Albums')
		self.clist.addItem('Top Artists')
		self.clist.addItem('Top Tracks')
		self.view = "Browse_newreleases"
		self.win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
		self.win.setProperty("view", self.view)
		print "onInit(): Window initialized"
		print "Starting the engines"
		self.main()

	def main(self):
		print "self.win view property is "+self.win.getProperty("view")
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
		if self.view == "Browse_newreleases":
			#print "self.view = "+self.view
			#app.save_album_data()
			app.set_var(list, app.newreleases__)
			self.getControl(300).setVisible(True)
			self.getControl(50).setVisible(True)
			alb.get_newreleases(self)
		if self.view == "Browse_topalbums":
			#app.save_album_data()
			app.set_var(list, app.topalbums__)
			self.getControl(300).setVisible(True)
			self.getControl(50).setVisible(True)
			alb.get_topalbums(self)


	def onAction(self, action):
		print str(action.getId())
		print type(action)
		if action.getId() == 7:
			if self.getFocusId() == 201:
				print "onAction(): Clicked a menu item!"
				print "onAction(): Item: " + str(self.getFocus(201).getSelectedPosition())
				menuitem = self.getFocus(201).getSelectedPosition()
				self.view = self.browse_list[menuitem]
				self.win.setProperty("view", self.view)
				self.main()
			if self.getFocusId() == 1001:
				app.set_var('logged_in', False)
				#player.stop()
				#alb.playlist.clear()
				self.close()
		if action.getId() == 10:
			#app.save_album_data()
			app.set_var('running',False)
			#player.stop()
			#alb.playlist.clear()
			self.close()
		elif action.getId() == 92:
			#app.save_album_data()
			#xbmc.executebuiltin("ActivateWindow(yesnodialog)")
			app.set_var('running',False)
			#player.stop()
			#alb.playlist.clear()
			self.close()
		else:
			pass


	def onClick(self, control):
		print "onclick(): control %i" % control
		self.pos = self.getCurrentListPosition()
		if control == 50:
			print "Opening album detail dialog"
			#print str(app.get_var(list))
			self.alb_dialog = AlbumDialog("album.xml", __addon_path__, 'Default', '720p', current_list=app.get_var(list),
			                         pos=self.pos)
			self.alb_dialog.setProperty("review", "has_review")
			self.alb_dialog.doModal()
			del self.alb_dialog
		if control == 201:
			print "I see you've clicked the nav menu"

	def onFocus(self, control):
		#print("onfocus(): control %i" % control)
		pass


class DialogBase(xbmcgui.WindowXMLDialog):
	def __init__(self, xmlName, thescriptPath, defaultname, forceFallback):
		print "I'm the base dialog class"


class AlbumDialog(DialogBase):
	def __init__(self, *args, **kwargs):
		DialogBase.__init__(self, *args)
		self.current_list = kwargs.get('current_list')
		self.pos = kwargs.get('pos')
		self.img_dir = __addon_path__+'/resources/skins/Default/media/'
		#win.current_playlist_albumId



	def onInit(self):
		#self.win = xbmcgui.WindowDialog(xbmcgui.getCurrentWindowDialogId())
		self.clearList()
		self.show_info()




	def show_info(self):
		self.populate_fields()
		alb.get_large_art(self.current_list, self.pos)
		self.populate_fields()
		alb.get_album_review(self.current_list, self.pos)
		print self.getProperty("review")
		self.populate_fields()
		alb.get_album_details(self.current_list, self.pos)
		self.populate_fields()
		alb.get_album_tracklist(self.current_list, self.pos, self)
		#print "focus id: "+str(self.getFocusId())


	def onAction(self, action):
		#print str(action.getId())
		#print type(action)
		# --- Enter / Select ---
		if action.getId() == 7:
			# ---Play Button ---
			if self.getFocusId() == 21:
				alb.get_album_playlist(self.current_list, self.pos, self)
				player.add_playable_track(0,0)
				player.playselected(0)
				self.setCurrentListPosition(alb.playlist.getposition())
				self.setFocusId(51)
				player.add_playable_track(self.getCurrentListPosition(),1)
				#player.play(alb.playlist)
				#print "---------------Started playlist from dialog play button. Current playlist position is: "+str(alb.playlist.getposition())
				#print "---------------Current window list position is: "+str(self.getCurrentListPosition())
				#print "---------------Current playlist album is: "+win.current_playlist_albumId
				#print "---------------Current dialog album is: "+self.current_list[self.pos]["album_id"]
			# --- Next Button---
			elif self.getFocusId() == 27:
				self.clearList()
				#print "self.pos before: "+str(self.pos)
				#print "Album_id before: "+self.current_list[self.pos]["album_id"]
				self.pos = (self.pos+1) % len(self.current_list)
				win.pos = self.pos
				#print "self.pos after:  "+str(self.pos)
				#print "Album_id after: "+self.current_list[self.pos]["album_id"]
				#player.sync_current_list_pos()
				self.show_info()
			# --- Prev Button ---
			elif self.getFocusId() == 26:
				self.clearList()
				self.pos = (self.pos-1) % len(self.current_list)
				win.pos = self.pos
				#player.sync_current_list_pos()
				self.show_info()
			# --- tracklist ---
			elif self.getFocusId() == 51:
				#print "Clicked on track # "+str(self.getCurrentListPosition()+1)
				#print "track_id is: "+self.current_list[self.pos]['tracks'][self.getCurrentListPosition()]['trackId']
				if win.current_playlist_albumId != self.current_list[self.pos]["album_id"]:
					alb.get_album_playlist(self.current_list, self.pos, self)
					#print "updating playlist with selected album"
				print "Playlist has "+str(len(alb.playlist))+" songs"
				player.add_playable_track(self.getCurrentListPosition(),0)
				player.playselected(self.getCurrentListPosition())
				if self.getCurrentListPosition()+1 < len(alb.playlist):
					player.add_playable_track(self.getCurrentListPosition(),1)
				else:
					print "At end of tracklist. Prefetch first song in case repeat is on"
					player.add_playable_track(0,0)
				print "Playlist still has "+str(len(alb.playlist))+" songs"

			else: pass
		elif action.getId() == 10:
			self.close()
		elif action.getId() == 92:
			self.close()
		else:
			pass


	#def onFocus(self, control):
		#print("onfocus(): control %i" % control)


	def populate_fields(self):
		#print "current list length: "+str(len(self.current_list))
		#print "current self.pos: "+str(self.pos)
		self.getControl(6).setLabel(self.current_list[self.pos]["style"])
		self.getControl(7).setImage(self.current_list[self.pos]["bigthumb"])
		self.getControl(8).setLabel(self.current_list[self.pos]["album_date"])
		if self.current_list[self.pos]["orig_date"]:
			self.getControl(9).setLabel("Original Release: " + self.current_list[self.pos]["orig_date"])
		self.getControl(10).setLabel(self.current_list[self.pos]["label"])
		self.getControl(11).setText(self.current_list[self.pos]["album"])
		self.getControl(13).setLabel(self.current_list[self.pos]["artist"])
		self.getControl(14).setText(self.current_list[self.pos]["review"])


class Member():
	def __init__(self):
		self.info = []
		self.filename = __addon_path__+'/resources/.rhapuser.obj'
		self.picklefile = ''
		self.olddevkey = "5C8F8G9G8B4D0E5J"
		self.cobrandId = "40134"
		self.user_info = {}
		self.username = ""
		self.password = ""
		self.access_token = ""
		self.refresh_token = ""
		self.issued_at = ""
		self.expires_in = ""
		self.guid = ""
		self.account_type = "Not available"
		self.date_created = "Not available"
		self.first_name = ""
		self.last_name = ""
		self.catalog = ""
		self.timestamp = ""


	def has_saved_creds(self):
		print "checking saved creds"
		try:
			self.user_info = pickle.load(open(self.filename, 'rb'))
			print "I see the cred file. Here's the contents:"
			prettyprint(self.user_info)
			self.username = self.user_info['username']
			self.password = base64.b64decode(self.user_info['password'])
			self.guid = self.user_info['guid']
			self.access_token = self.user_info['access_token']
			self.refresh_token = self.user_info['refresh_token']
			self.issued_at = self.user_info['issued_at']
			self.expires_in = self.user_info['expires_in']
			self.first_name = self.user_info['first_name']
			self.last_name = self.user_info['last_name']
			self.catalog = self.user_info['catalog']
			self.timestamp = self.user_info['timestamp']
		except:
			print "Couldn't read saved user data. Login please"
			return False
		print "current time: "+str(time.time())
		print "creds time: "+str(self.timestamp)
		if time.time() - self.timestamp < self.expires_in:
			print "Saved creds look good. Automatic login successful!"
			app.set_var('logged_in', True)
			return True
		else:
			print "Saved creds have expired. Generating new ones."
			self.login_member(self.username, self.password)

	def save_user_info(self):
		#print "Adding data to user_info object"
		self.user_info['username'] = self.username
		self.user_info['password'] = base64.b64encode(self.password)
		self.user_info['guid'] = self.guid
		self.user_info['access_token'] = self.access_token
		self.user_info['refresh_token'] = self.refresh_token
		self.user_info['issued_at'] = self.issued_at
		self.user_info['expires_in'] = self.expires_in
		self.user_info['first_name'] = self.first_name
		self.user_info['last_name'] = self.last_name
		self.user_info['catalog'] = self.catalog
		self.user_info['timestamp'] = time.time()
		#prettyprint(self.user_info)
		print "Saving userdata..."
		pickle.dump(self.user_info, open(self.filename, 'wb'))
		#print "Userdata saved!"


	def login_member(self, name, pswd):
		print "attempting login..."
		self.username = name
		self.password = pswd
		data = urllib.urlencode({'username': self.username, 'password': self.password, 'grant_type': 'password'})
		header = b'Basic ' + base64.b64encode(app.get_var('APIKEY') + b':' + app.get_var('SECRET'))
		result = "Bad username/password combination"

		req = urllib2.Request(app.get_var('AUTHURL'), data)
		req.add_header('Authorization', header)
		try:
			response = urllib2.urlopen(req)
			print "got response from login server"
			if response:
				result = json.load(response)
				self.access_token =     result["access_token"]
				self.catalog =          result["catalog"]
				self.expires_in =       result["expires_in"]
				self.first_name =       result["first_name"]
				self.guid =             result["guid"]
				self.issued_at =        result["issued_at"]
				self.last_name =        result["last_name"]
				self.refresh_token =    result["refresh_token"]
				app.set_var('logged_in', True)
				app.set_var('bad_creds', False)
				self.save_user_info()
		except: #urllib2.HTTPError, e:
			print "login failed"
			#print e.headers
			#print e
			app.set_var('logged_in', False)
			app.set_var('bad_creds', True)
		#prettyprint(result)


class Album():

	def __init__(self):
		self.playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)

	def get_big_image(self, albumid, img_dir):
		results = []
		print "finding largest image with API call"
		try:
			url = "%salbums/%s/images?apikey=%s" %(app.get_var('BASEURL'), albumid, app.get_var('APIKEY'))
			response = urllib2.urlopen(url)
			results = json.load(response)
		except:
			print "Bad server response getting large art info"
		if results:
			#prettyprint(results)
			biggest = 0
			biggest_index = 0
			for y in xrange(0, len(results)):
				s = results[y]["width"]
				if (s > biggest):
					biggest = s
					biggest_index = y
			biggest_image = results[biggest_index]["url"].split('/')[
				(len(results[biggest_index]["url"].split('/'))) - 1]
			img_url = results[biggest_index]["url"]
			img_file = img_dir + biggest_image
			if not os.path.isfile(img_file):
				print ("We need to get this file! Starting download")
				while not os.path.isfile(img_file):
					try:
						urllib.urlretrieve(img_url, img_file)
						print ("Downloaded the file :-)")
					except:
						print "File download failed"
						album_img = "AlbumPlaceholder.png"
						return album_img
			else:
				print ("Already have that file! Moving on...")
			return "album/" + biggest_image
		else:
			return "AlbumPlaceholder.png"


	def get_album_review(self, list, pos):
		results = []
		alb_id = list[pos]["album_id"]
		out = ""
		if not (app.album[alb_id]["review"] == ""):
			list[pos]["review"] = app.album[alb_id]["review"]
			print "Using saved review from album cache"
			return out
		elif list[pos]["review"] == "":
			try:
				#url = "http://direct.rhapsody.com/metadata/data/methods/getAlbumReview.js?developerKey=9H9H9E6G1E4I5E0I&albumId=%s&cobrandId=40134" % (newreleases[pos]["album_id"])
				url = "%salbums/%s/reviews?apikey=%s" % (app.get_var('BASEURL'), list[pos]["album_id"], app.get_var('APIKEY'))
				response = urllib2.urlopen(url)
				results = json.load(response)
			except:
				print "Review api not returning response"
			if results:
				print "got review from API call"
				list[pos]["review"] = remove_html_markup(results[0]["body"])
				return out
			else:
				print "Tried API. No review for this album"
				list[pos]["review"] = ""
				return out
		else:
			print "Already have the review in memory for this album"


	def get_album_details(self, list, pos):
		data = []
		alb_id = list[pos]["album_id"]
		print alb_id
		if list[pos]["label"] == "":
			# try to get info from cached album data
			if app.album.has_key(alb_id) and (app.album[alb_id]['label'] != ""):
				print "getting info from cached album data"
				list[pos]["label"] = app.album[alb_id]["label"]
				list[pos]["tracks"] = app.album[alb_id]["tracks"]
				list[pos]["style"] = app.album[alb_id]["style"]
				#prettyprint(list[pos]["tracks"])
			else:
				print "Getting genre, tracks and label with API call"
				try:
					url = "http://direct.rhapsody.com/metadata/data/methods/getAlbum.js?developerKey=9H9H9E6G1E4I5E0I&albumId=%s&cobrandId=40134&filterRightsKey=0" % (list[pos]["album_id"])
					#url = "%salbums/%s?apikey=%s" %(app.get_var('BASEURL'), newreleases[pos]["album_id"], app.get_var('APIKEY'))
					response = urllib2.urlopen(url)
					data = json.load(response)
				except:
					print "Album Detail api not returning response"
				if data:
					#prettyprint(data)
					#orig_date = time.strftime('%B %Y', time.localtime(int(data["originalReleaseDate"]["time"]) / 1000))
					#if newreleases[pos]["album_date"] != orig_date:
						#newreleases[pos]["orig_date"] = orig_date
					list[pos]["label"] = data["label"]
					list[pos]["tracks"] = data["trackMetadatas"]
					list[pos]["style"] = data["primaryStyle"]
					#print "Got label and original date for album"
				#prettyprint(list[pos]["tracks"])
		else:
			print "Already have label info for this album"



	def get_large_art(self, list, pos):
		image_dir = verify_image_dir()
		alb_id = list[pos]["album_id"]
		print "Thumb value: "+app.album[alb_id]['bigthumb']
		if os.path.isfile(image_dir + app.album[alb_id]['bigthumb'][6:]):
			print "Using cached image for cover art: " + app.album[alb_id]['bigthumb']
			list[pos]["bigthumb"] = app.album[alb_id]['bigthumb']
			#pass
		else:
			print "Getting album art with API call"
			file = self.get_big_image(list[pos]["album_id"], image_dir)
			list[pos]["bigthumb"] = file
			#print "Big Thumb: " + newreleases[pos]["bigthumb"]

	def get_newreleases(self, mainwin):
		print "entered get_newreleases"
		if (len(app.newreleases_listitems)) > 2:
			#rebuild window list from topalbums_listitems
			self.rebuild_window_list_from_listitems(app.newreleases_listitems)
			return
		else:
			#need to build newreleases list
			#check if newrelease__ is already present
			if app.newreleases__:
				#iterate through newreleases__ and build newreleases_list
				for item in app.newreleases__:
					listitem = xbmcgui.ListItem(item["album"], item["artist"], '', item['thumb'])
					app.newreleases_listitems.append(listitem)
				self.rebuild_window_list_from_listitems(app.newreleases_listitems)
				print "rebuilt list of newreleases listitems and populated win list"
				return
			else:
				mainwin.clearList()
				img_dir = verify_image_dir()
				default_album_img = __addon_path__+'/resources/skins/Default/media/'+"AlbumPlaceholder.png"
				results = ""
				count = 0
				try:
					url = '%salbums/new?apikey=%s&limit=100' % (app.get_var('BASEURL'), app.get_var('APIKEY'))
					response = urllib2.urlopen(url)
					results = json.load(response)
				except:
					print("Error when fetching Rhapsody data from net")
				if results:
					#print results["albums"][3]
					for item in results:
						img_file = item["images"][0]["url"].split('/')[(len(item["images"][0]["url"].split('/'))) - 1]
						img_path = img_dir + img_file
						data = self.get_alb_and_build_listitem(img_path, img_file, count, item, default_album_img)
						app.newreleases__.append(data['album'])
						app.newreleases_listitems.append(data['listitem'])
						#print "Added album to list control"
						mainwin.addItem(data['listitem'])
						if not app.album.has_key(item["id"]):
							app.album[item["id"]] = data['album']
							#print 'added an album to app.album'
						#else:
						#	print 'album already in app.album'
						count += 1
					#print "saving newreleasesdata"
					#app.save_newreleases_data()
					app.save_album_data()


				#prettyprint(app.album["Alb.122693202"])
				#prettyprint(app.album.keys())


	def get_topalbums(self, mainwin):
		if (len(app.topalbums_listitems)) > 2:
			#rebuild window list from topalbums_listitems
			self.rebuild_window_list_from_listitems(app.topalbums_listitems)
			return
		else:
			#need to build topalbums list
			#check if topalbums__ is already present
			if app.topalbums__:
				#iterate through topalbum__s and build topalbums_list
				for item in app.topalbums__:
					listitem = xbmcgui.ListItem(item["album"], item["artist"], '', item['thumb'])
					app.topalbums_listitems.append(listitem)
				self.rebuild_window_list_from_listitems(app.topalbums_listitems)
				print "rebuilt list of  topalbums listitems and populated win list"
				return
			else:
				#start from scratch with API call for newreleases
				img_dir = verify_image_dir()
				default_album_img = __addon_path__+'/resources/skins/Default/media/'+"AlbumPlaceholder.png"
				results = ""
				count = 0
				try:
					url = '%salbums/top?apikey=%s&limit=100' % (app.get_var('BASEURL'), app.get_var('APIKEY'))
					response = urllib2.urlopen(url)
					results = json.load(response)
				except:
					print("Error when fetching Rhapsody data from net")
				if results:
					#print results["albums"][3]
					mainwin.clearList()
					for item in results:
						img_file = item["images"][0]["url"].split('/')[(len(item["images"][0]["url"].split('/'))) - 1]
						img_path = img_dir + img_file
						data = self.get_alb_and_build_listitem(img_path, img_file, count, item, default_album_img)
						app.topalbums__.append(data['album'])
						app.topalbums_listitems.append(data['listitem'])
						#print "Added album to list control"
						mainwin.addItem(data['listitem'])
						if not app.album.has_key(item["id"]):
							app.album[item["id"]] = data['album']
							print 'added an album to app.album'
						else:
							print 'album already in app.album'
						count += 1
					#print "saving topalbumsdata"
					#app.save_topalbums_data()
					app.save_album_data()

	def get_alb_and_build_listitem(self, img_path, img_file, count, item, default_album_img):
		data = {}
		if not os.path.isfile(img_path):
			try :
				print ("We need to get album art for " + item["name"] + ". Starting download")
			except:
				print "We need to get album art for a non-ascii album title. Starting download"
			#xbmc.log(msg=mess, level=xbmc.LOGDEBUG)
			try:
				while not os.path.isfile(img_path):
					urllib.urlretrieve(item["images"][0]["url"], img_path)
					print("Downloaded " + img_file)
					album = {'album_id': item["id"],
					         'album': item["name"],
					         'thumb': "album/" + img_file,
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
					listitem = xbmcgui.ListItem(item["name"], item["artist"]["name"], '', "album/" + img_file)
			except:
				try:
					print("Album art not available for " + item["name"] + ". Using default album image")
				except:
					print "Album art not available for non-ascii album title. Using default album image"
				album = {'album_id': item["id"],
				         'album': item["name"],
				         'thumb': default_album_img,
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
				listitem = xbmcgui.ListItem(item["name"], item["artist"]["name"], '', default_album_img)
		else:
			#print("Already have album art for " + item["name"] + ". Moving on...")
			album = {'album_id': item["id"],
			         'album': item["name"],
			         'thumb': "album/" + img_file,
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
			listitem = xbmcgui.ListItem(item["name"], item["artist"]["name"], '', "album/" + img_file)
		data['album'] = album
		data['listitem'] = listitem
		return data


	def rebuild_window_list_from_listitems(self, list_of_listitems):
		win.clearList()
		for x in range (0, len(list_of_listitems)):
			win.addItem(list_of_listitems[x])
		print "populated the window listcontrol with cached listitems"

	def get_topartists(self, mainwin, member):
		pass

	def get_toptracks(self, mainwin, member):
		pass

	def get_album_tracklist(self, album_list, pos, albumdialog):

		x = 0
		for item in album_list[pos]["tracks"]:
			newlistitem = xbmcgui.ListItem(path="http://dummyurl.org")
			newlistitem.setInfo('music', { 'tracknumber':   int(album_list[pos]["tracks"][x]["trackIndex"]),
			                               'title':         album_list[pos]["tracks"][x]["name"],
			                               'duration':      int(album_list[pos]["tracks"][x]["playbackSeconds"])
			                               })
			albumdialog.addItem(newlistitem)
			x += 1
		print "Added "+str(x)+"tracks to list"
		player.sync_current_list_pos()

	def get_album_playlist(self, album_list, pos, albumdialog):

		self.playlist.clear()
		x = 0
		for item in album_list[pos]["tracks"]:
			self.playlist.add(album_list[pos]["tracks"][x]["previewURL"], listitem=xbmcgui.ListItem(''))
			#name = "track"+str(x)
			#self.playlist.add(name, listitem=xbmcgui.ListItem(''))
			x += 1
		print "Added "+str(x)+"tracks to playlist for "+album_list[pos]["album_id"]
		win.current_playlist_albumId = album_list[pos]["album_id"]




class Genres():
	def __init__(self):
		#self.get_genre_tree()
		#self.flatten_genre_keys(app.genre_tree__)
		#app.save_genre_data()
		pass


	def get_genre_tree(self):
		results = None
		try:
			url = "%sgenres?apikey=%s" % (app.get_var('BASEURL'), app.get_var('APIKEY'))
			response = urllib2.urlopen(url)
			results = json.load(response)
		except:
			print "Genres api not returning response"

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

	def onQueueNextItem(self):
		print "Rhapsody knows the next track has been queued"

	def onPlayBackStarted(self):
		#print "-----------OnPlaybackStarted: Attempting to set albdialog list focus---------------"
		#print "-----------Current playlist albumID: "+str(win.current_playlist_albumId)
		#print "-----------Current dialog albumId:   "+str(win.current_list[win.alb_dialog.pos]["album_id"])
		self.sync_current_list_pos()
		#info = xbmc.InfoTagMusic()
		#print "--------- Infotags ---------"
		#print info.getAlbum()
		#print info.getArtist()
		#print info.getTitle()
		#print str(info.getTrack())

	def sync_current_list_pos(self):
		#print "-------------checking if we need to  sync list position"
		#print "playlist: "+win.current_playlist_albumId+"  dialoglist: "+win.alb_dialog.current_list[win.alb_dialog.pos]["album_id"]
		if win.current_playlist_albumId == win.alb_dialog.current_list[win.alb_dialog.pos]["album_id"]:
			#print "albums match. let's try to sync"
			#print "Current focused song position: "+str(win.alb_dialog.getCurrentListPosition()+1)
			win.alb_dialog.setCurrentListPosition(alb.playlist.getposition())
			#win.alb_dialog.setFocusId(51)
			#print "sync complete. Should have worked! Set position to track "+str(alb.playlist.getposition()+1)
		#else:
		#	print "albums don't match - no list sync necessary"

	def get_playback_session(self):
		print 'curl -v -H "Authorization: Bearer 1l1iEkDO0hV9sjLJlSAmmH1Auw4B" https://api.rhapsody.com/v1/play/Tra.44464021'

	def get_playable_url(self, track_id):
		url = "%splay/%s" %(app.get_var('S_BASEURL'), track_id)
		#print "Trying to get this track url: "+url
		header = b'Bearer ' + mem.access_token
		req = urllib2.Request(url)
		req.add_header('Authorization', header)

		#print "getting playable URL for track"
		try:
			response = urllib2.urlopen(req)
			#print "got response!"
			if response:
				#print "got results!"
				results = json.load(response)
				#print "------------------"+results['url']
				#print "------------------"+results['format']
				#print "------------------"+str(results['bitrate'])
				return results['url']
		except urllib2.HTTPError, e:
			print "------------------  Bad server response getting playable URL"
			print e.headers
			print e
			return None

	def add_playable_track(self, pos, offset):
		#print "!!!! -------- Current playlist item filename: "+alb.playlist.__getitem__(pos+offset).getfilename()
		tid = app.get_var(list)[win.pos]['tracks'][pos+offset]['trackId']
		tname = alb.playlist.__getitem__(pos+offset).getfilename()
		playurl = player.get_playable_url(tid)
		alb.playlist.remove(tname)
		alb.playlist.add(playurl, listitem=xbmcgui.ListItem(''), index=pos+offset)

def GetStringFromUrl(encurl):
	doc = ""
	succeed = 0
	while succeed < 5:
		try:
			f = urllib.urlopen(encurl)
			doc = f.read()
			f.close()
			return str(doc)
		except:
			xbmc.log("could not get data from %s" % encurl)
			xbmc.sleep(1000)
			succeed += 1
	return ""


def prettyprint(string):
	print(json.dumps(string, sort_keys=True, indent=4, separators=(',', ': ')))


def verify_image_dir():
	img_dir = __addon_path__+'/resources/skins/Default/media/album/'
	if (not os.path.isdir(img_dir)):
		os.mkdir(img_dir)
		print ("Created the missing album image directory at " + img_dir)
	else:
		print "Image directory is present!"
	return img_dir


def remove_html_markup(s):
	tag = False
	quote = False
	out = ""
	for c in s:
		if c == '<' and not quote:
			tag = True
		elif c == '>' and not quote:
			tag = False
		elif (c == '"' or c == "'") and tag:
			quote = not quote
		elif not tag:
			out = out + c
	return out


def main(win, loadwin):
	print "creating main window"
	print "going modal with main window"
	win.doModal()
	del win
	print "main window has closed"
	#app.save_album_data()
	del loadwin
	print "loading window has closed"
	gc.collect()
	print "Collecting garbage"



app = Application()
mem = Member()
alb = Album()
genres = Genres()
player = Player()


app.set_var("BASEURL", "http://api.rhapsody.com/v1/")
app.set_var("S_BASEURL", "https://api.rhapsody.com/v1/")
app.set_var("AUTHURL", "https://api.rhapsody.com/oauth/token")
app.set_var("APIKEY",  "22Q1bFiwGxYA2eaG4vVAGsJqi3SQWzmd")
app.set_var("SECRET",  "Z1AAYBC1JEtnMJGm")
app.set_var('running', True)
app.set_var('logged_in', False)
app.set_var('bad_creds', False)

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
	win = MainWin("main.xml", __addon_path__, 'Default', '720p')
	win.doModal()
	if app.get_var('logged_in') == False:
		loadwin.getControl(10).setLabel('Logging you out...')
	else:
		loadwin.getControl(10).setLabel('Finishing up...')
	del win
	time.sleep(1)
	app.save_album_data()
del loadwin
gc.collect()
print "App has been exited"


