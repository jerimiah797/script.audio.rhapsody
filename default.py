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
from lib import rhapapi


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
		self.__vars = {}  #dict for app vars
		self.user_data = {} #object to store cached data

		self.newreleases__ = []  #json data from rhapsody
		self.newreleases_listitems = []  #listitems for album window list
		self.newreleases = {} #object to store cached data
		self.newreleases_file = __addon_path__+'/resources/.newreleases.obj' #picklefile

		self.toptracks__ = []  #json data from rhapsody
		self.toptracks_listitems = []  #listitems for album window list

		self.topalbums__ = []  #json data from rhapsody
		self.topalbums_listitems = []  #listitems for album window list
		self.topalbums = {}  #object to store cached data
		self.topalbums_file = __addon_path__+'/resources/.topalbums.obj'  #picklefile

		self.topartists__ = []  #json data from rhapsody
		self.topartists_listitems = []  #listitems for album window list

		self.genre_tree__ = []  #json data from rhapsody
		self.genre_dict__ = {}  #object to store cached data

		self.artist = {}  #object to store cached data

		self.album = {}  #object to store cached data
		self.album_file = __addon_path__+'/resources/.albumdb.obj'  #picklefile

		self.genre = {}  #object to store cached data
		self.genre_file = __addon_path__+'/resources/.genres.obj'  #picklefile

		self.now_playing = {'pos': 0, 'type': None,'item':[]}
		self.onplay_lock = False
		self.album_art_path = __addon_path__+"/resources/skins/Default/media/"


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

		#try:
		#	self.newreleases = pickle.load(open(self.newreleases_file, 'rb'))
		#	self.newreleases__ = self.newreleases['newreleases']
		#	print "Loaded New Releases cache"
		#except:
		#	print "Couldn't read new releases cache file. Skipping..."
		#
		#try:
		#	self.topalbums = pickle.load(open(self.topalbums_file, 'rb'))
		#	self.topalbums__ = self.topalbums['topalbums']
		#	print "Loaded Top Albums cache"
		#except:
		#	print "Couldn't read top albums cache file. Skipping..."


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
		print "Script path: " + __addon_path__


	def onInit(self):
		self.clist = self.getControl(201)
		self.clist.addItem('New Releases')
		self.clist.addItem('Top Albums')
		self.clist.addItem('Top Artists')
		self.clist.addItem('Top Tracks')
		self.win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
		self.win.setProperty("view", app.get_var('view'))
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
				self.win.setProperty("view", app.get_var('view'))
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
			#app.save_album_data()
			app.set_var('running',False)
			player.stop()
			playlist.clear()
			self.close()
		elif action.getId() == 92:
			#app.save_album_data()
			#xbmc.executebuiltin("ActivateWindow(yesnodialog)")
			app.set_var('running',False)
			player.stop()
			playlist.clear()
			self.close()
		else:
			pass


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
			self.setCurrentListPosition(self.pos)
			del self.alb_dialog
			app.save_album_data()
		#if control == 201:
		#	print "I see you've clicked the nav menu"

	def onFocus(self, control):
		#print("onfocus(): control %i" % control)
		pass

	def draw_newreleases(self):
		app.set_var(list, app.newreleases__)
		self.getControl(300).setVisible(True)
		self.getControl(50).setVisible(True)
		alb.get_newreleases()

	def draw_topalbums(self):
		app.set_var(list, app.topalbums__)
		self.getControl(300).setVisible(True)
		self.getControl(50).setVisible(True)
		alb.get_topalbums()

	def draw_mainwin_browse(self):
		if app.get_var('view') == "Browse_newreleases":
			#app.save_album_data()
			self.draw_newreleases()
			self.setFocusId(50)
			if self.pos:
				self.setCurrentListPosition(self.pos)
		if app.get_var('view') == "Browse_topalbums":
			#app.save_album_data()
			self.draw_topalbums()
			self.setFocusId(50)
			if self.pos:
				self.setCurrentListPosition(self.pos)


class DialogBase(xbmcgui.WindowXMLDialog):
	def __init__(self, xmlName, thescriptPath, defaultname, forceFallback):
		#print "I'm the base dialog class"
		pass


class AlbumDialog(DialogBase):
	def __init__(self, *args, **kwargs):
		DialogBase.__init__(self, *args)
		self.current_list = kwargs.get('current_list')
		#self.pos = kwargs.get('pos')
		#self.pos = win.pos
		self.img_dir = __addon_path__+'/resources/skins/Default/media/'


	def onInit(self):
		self.clearList()
		self.show_info()


	def show_info(self):
		self.populate_fields()
		#alb_id = self.current_list[win.pos]['album_id']
		#print "show_info albub id: "+alb_id
		alb.get_large_art(self.current_list, win.pos)
		self.populate_fields()
		alb.get_album_review(self.current_list, win.pos)
		self.populate_fields()
		alb.get_album_details(self.current_list, win.pos)
		self.populate_fields()
		alb.get_album_tracklist(self.current_list, win.pos, self)


	def onAction(self, action):
		#print str(action.getId())
		#print type(action)
		# --- Enter / Select ---
		if action.getId() == 7:
			# ---Play Button ---
			if self.getFocusId() == 21:
				print "Assigning album "+self.current_list[win.pos]['album_id']+" to app.now_playing"
				app.now_playing['type'] = "album"
				app.now_playing['item'] = self.current_list[win.pos]
				app.now_playing['pos'] = 0
				#prettyprint(app.now_playing)
				#win.playing_pos = win.pos
				#alb.populate_album_playlist(self.current_list, win.pos)
				populate_playlist()
				add_playable_track(0)
				player.playselected(0)
				self.setCurrentListPosition(playlist.getposition())
				self.setFocusId(51)
			# --- Next Button---
			elif self.getFocusId() == 27:
				self.clearList()
				win.pos = (win.pos+1) % len(self.current_list)
				self.show_info()
			# --- Prev Button ---
			elif self.getFocusId() == 26:
				self.clearList()
				win.pos = (win.pos-1) % len(self.current_list)
				self.show_info()
			# --- tracklist ---
			elif self.getFocusId() == 51:
				if app.now_playing['item']['album_id'] != self.current_list[win.pos]["album_id"]:
					app.now_playing['type'] = "album"
					app.now_playing['item'] = self.current_list[win.pos]
					app.now_playing['pos'] = 0
					populate_playlist()
				#win.playing_pos = win.pos
				app.now_playing['pos'] = self.getCurrentListPosition()
				add_playable_track(0)
				player.playselected(app.now_playing['pos'])
			else: pass
		elif action.getId() == 10:
			self.close()
		elif action.getId() == 92:
			self.close()
		elif action.getId() == 18:
			self.close()
		else:
			pass


	def populate_fields(self):
		#print "current list length: "+str(len(self.current_list))
		#print "current self.pos: "+str(self.pos)
		self.getControl(6).setLabel(self.current_list[win.pos]["style"])
		self.getControl(7).setImage(self.current_list[win.pos]["bigthumb"])
		self.getControl(8).setLabel(self.current_list[win.pos]["album_date"])
		if self.current_list[win.pos]["orig_date"]:
			self.getControl(9).setLabel("Original Release: " + self.current_list[win.pos]["orig_date"])
		self.getControl(10).setLabel(self.current_list[win.pos]["label"])
		self.getControl(11).setText(self.current_list[win.pos]["album"])
		self.getControl(13).setLabel(self.current_list[win.pos]["artist"])
		self.getControl(14).setText(self.current_list[win.pos]["review"])


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
			print "Using saved user credentials for "+self.user_info['username']
			#prettyprint(self.user_info)
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
		#print "current time: "+str(time.time())
		#print "creds time: "+str(self.timestamp)
		#print "Expires in: "+str(self.expires_in)
		#print "Difference: "+str(time.time()-self.timestamp)
		diff = time.time()-self.timestamp
		if diff < self.expires_in:
			print "Saved creds look good. Automatic login successful!"
			app.set_var('logged_in', True)
			return True
		else:
			print "Saved creds have expired. Generating new ones."
			self.login_member(self.username, self.password)
			return True

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
						#return img_dir+img_file
					except:
						print "File download failed"
						album_img = "AlbumPlaceholder.png"
						return album_img
			else:
				print ("Already have that file! Moving on...")
			return img_dir + biggest_image
		else:
			return "AlbumPlaceholder.png"


	def get_album_review(self, list, pos):
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


	def get_album_details(self, list, pos):
		data = []
		alb_id = list[pos]["album_id"]
		#print alb_id
		if list[pos]["label"] == "":
			# try to get info from cached album data
			if app.album.has_key(alb_id) and (app.album[alb_id]['label'] != ""):
				print "Using genre, track, and label from cached album data"
				list[pos]["label"] = app.album[alb_id]["label"]
				list[pos]["tracks"] = app.album[alb_id]["tracks"]
				list[pos]["style"] = app.album[alb_id]["style"]
				#prettyprint(list[pos]["tracks"])
			else:
				print "Getting genre, tracks and label from Rhapsody"
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
					app.album[alb_id]['label'] = data['label']
					list[pos]["tracks"] = data["trackMetadatas"]
					app.album[alb_id]["tracks"] = data["trackMetadatas"]
					list[pos]["style"] = data["primaryStyle"]
					app.album[alb_id]["style"] = data["primaryStyle"]
					#print "Got label and original date for album"
				#prettyprint(list[pos]["tracks"])
		else:
			print "Using genre, track, and label from cached album data"



	def get_large_art(self, list, pos):
		image_dir = verify_image_dir('large/')
		#print "Image dir: "+image_dir
		alb_id = list[pos]["album_id"]
		print alb_id
		print "Existing BigThumb value: "+app.album[alb_id]['bigthumb']
		print "Testing for "+app.album[alb_id]['bigthumb']
		if os.path.isfile(app.album[alb_id]['bigthumb']):
			print "Using image from cached album data" # at " + app.album[alb_id]['bigthumb']
			list[pos]["bigthumb"] = app.album[alb_id]['bigthumb']
			print "local list value:"+ list[pos]['bigthumb']
			print "album dialog bigthumb value: "+win.alb_dialog.current_list[pos]['bigthumb']
			#pass
		else:
			print "Getting album art from Rhapsody"
			file = self.get_big_image(list[pos]["album_id"], image_dir)
			list[pos]["bigthumb"] = file
			app.album[alb_id]['bigthumb'] = file
			print "New Big Thumb: " + app.album[alb_id]['bigthumb']

	def get_newreleases(self):
		print "Fetching New Releases"
		if (len(app.newreleases_listitems)) > 2:
			#rebuild window list from topalbums_listitems
			print "already have the list of listitems, so we're using that"
			self.rebuild_window_list_from_listitems(app.newreleases_listitems)
			return
		else:
			#need to build newreleases list
			#check if newrelease__ is already present
			if app.newreleases__:
				#iterate through newreleases__ and build newreleases_list
				print "building window list items"


				#x = 0
				#for item in app.newreleases__:
				#	if app.album[app.newreleases__[x]['album_id']]['bigthumb'] != "":
				#		thumb = app.album[app.newreleases__[x]['album_id']]['bigthumb']
				#	else:
				#		thumb = item['thumb']
				#	listitem = xbmcgui.ListItem(item["album"], item["artist"], '', thumb)
				#	app.newreleases_listitems.append(listitem)
				#	x += 1


				for item in app.newreleases__:
					listitem = xbmcgui.ListItem(item["album"], item["artist"], '', item['thumb'])
					app.newreleases_listitems.append(listitem)
				self.rebuild_window_list_from_listitems(app.newreleases_listitems)
				#print "rebuilt list of newreleases listitems and populated win list"
				return
			else:
				win.clearList()
				img_dir = verify_image_dir('')
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
						win.addItem(data['listitem'])
						if not app.album.has_key(item["id"]):
							app.album[item["id"]] = data['album']
							#print 'added an album to app.album'
						#else:
						#	print 'album already in app.album'
						count += 1
					print "saving newreleasesdata"
					app.save_newreleases_data()
					app.save_album_data()


				#prettyprint(app.album["Alb.122693202"])
				#prettyprint(app.album.keys())


	def get_topalbums(self):
		print "Fetching Top Albums"
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
				img_dir = verify_image_dir('')
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
					win.clearList()
					for item in results:
						img_file = item["images"][0]["url"].split('/')[(len(item["images"][0]["url"].split('/'))) - 1]
						img_path = img_dir + img_file
						data = self.get_alb_and_build_listitem(img_path, img_file, count, item, default_album_img)
						app.topalbums__.append(data['album'])
						app.topalbums_listitems.append(data['listitem'])
						#print "Added album to list control"
						win.addItem(data['listitem'])
						if not app.album.has_key(item["id"]):
							app.album[item["id"]] = data['album']
						#	print 'added an album to app.album'
						#else:
						#	print 'album already in app.album'
						count += 1
					print "saving topalbumsdata"
					app.save_topalbums_data()
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
		print "Using album list from cache"

	def get_topartists(self, mainwin, member):
		pass

	def get_toptracks(self, mainwin, member):
		pass

	def get_album_tracklist(self, album_list, pos, albumdialog):

		x = 0
		#prettyprint(album_list[pos]["tracks"])
		for item in album_list[pos]["tracks"]:
			newlistitem = xbmcgui.ListItem(path="http://dummyurl.org")
			newlistitem.setInfo('music', { 'tracknumber':   int(album_list[pos]["tracks"][x]["trackIndex"]),
			                               'title':         album_list[pos]["tracks"][x]["name"],
			                               'duration':      int(album_list[pos]["tracks"][x]["playbackSeconds"])
			                               })
			albumdialog.addItem(newlistitem)
			x += 1
		print "Album has "+str(x)+" tracks"
		sync_current_list_pos()

	#def populate_album_playlist(self, album_list, pos):
	#
	#	playlist.clear()
	#	x = 0
	#	for item in album_list[pos]["tracks"]:
	#		playlist.add("dummy"+str(x)+".mp3", listitem=xbmcgui.ListItem(''))
	#		x += 1
	#	print "Okay let's play some music! Added "+str(x)+" tracks to the playlist"# for "+album_list[pos]["album_id"]
	#	win.current_playlist_albumId = album_list[pos]["album_id"]



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

	def onPlayBackStarted(self):
		if not app.onplay_lock:
			app.onplay_lock = True
			sync_current_list_pos()
			pos = playlist.getposition()
			app.now_playing['pos'] = pos
			print "Playing track "+str(pos+1)
			add_playable_track(1)
			add_playable_track(-1)
			sync_current_list_pos()
			pos2 = playlist.getposition()
			#print "pos: "+str(pos)+" pos2: "+str(pos2)
			if pos != pos2:
				print "Oh wait! We're not playing track "+str(pos+1)+"!"
				print "Playing track "+str(pos2+1)
				print "There, fixed it for ya. "
				app.now_playing['pos'] = pos2
				add_playable_track(1)
				add_playable_track(-1)
			xbmc.sleep(2)
			app.onplay_lock = False
		else:
			print "--------- blocked an extra play action from XBMC --------"


	def onPlayBackResumed(self):
		if not app.onplay_lock:
			app.onplay_lock = True
			sync_current_list_pos()
			pos = playlist.getposition()
			app.now_playing['pos'] = pos
			print "Playing track "+str(pos+1)
			add_playable_track(1)
			add_playable_track(-1)
			sync_current_list_pos()
			pos2 = playlist.getposition()
			#print "pos: "+str(pos)+" pos2: "+str(pos2)
			if pos != pos2:
				print "Oh wait! We're not playing track "+str(pos+1)+"!"
				print "Playing track "+str(pos2+1)
				print "There, fixed it for ya. "
				app.now_playing['pos'] = pos2
				add_playable_track(1)
				add_playable_track(-1)
			xbmc.sleep(2)
			app.onplay_lock = False
		else:
			print "--------- blocked an extra play action from XBMC --------"

	def onPlayBackEnded(self):
		print "onPlaybackEnded was detected!"

	def onPlayBackStopped(self):
		print "onPlaybackStopped was detected!"

	def onQueueNextItem(self):
		print "onQueueNextItem was detected!"




def sync_current_list_pos():
	#print "-------------checking if we need to  sync list position"
	#print "playlist: "+win.current_playlist_albumId+"  dialoglist: "+win.alb_dialog.current_list[win.alb_dialog.pos]["album_id"]
	try:
		if win.current_playlist_albumId == win.alb_dialog.current_list[win.pos]["album_id"]:
			#print "albums match. let's try to sync"
			#print "Current focused song position: "+str(win.alb_dialog.getCurrentListPosition()+1)
			win.alb_dialog.setCurrentListPosition(playlist.getposition())
			#win.alb_dialog.setFocusId(51)
			#print "sync complete. Should have worked! Set position to track "+str(playlist.getposition()+1)
		#else:
		#	print "albums don't match - no list sync necessary"
	except:
		#print "No dialog window open, so don't need to sync dialog list"
		pass

def get_playback_session():
	print 'curl -v -H "Authorization: Bearer 1l1iEkDO0hV9sjLJlSAmmH1Auw4B" https://api.rhapsody.com/v1/play/Tra.44464021'

def populate_playlist():

		playlist.clear()
		x = 0
		for item in app.now_playing['item']['tracks']:
			playlist.add("dummy"+str(x)+".mp3", listitem=xbmcgui.ListItem(''))
			x += 1
		print "Okay let's play some music! Added "+str(x)+" tracks to the playlist for "+app.now_playing['item']["album_id"]
		win.current_playlist_albumId = app.now_playing['item']["album_id"]  #can probably eliminate this variable

#def get_playable_url(track_id):
#	url = "%splay/%s" %(app.get_var('S_BASEURL'), track_id)
#	#print "Trying to get this track url: "+url
#	header = b'Bearer ' + mem.access_token
#	req = urllib2.Request(url)
#	req.add_header('Authorization', header)
#
#	#print "getting playable URL for track"
#	try:
#		response = urllib2.urlopen(req)
#		#print "got response!"
#		if response:
#			#print "got results!"
#			results = json.load(response)
#			#print "------------------"+results['url']
#			#print "------------------"+results['format']
#			#print "------------------"+str(results['bitrate'])
#			return results['url']
#	except urllib2.HTTPError, e:
#		print "------------------  Bad server response getting playable URL"
#		print e.headers
#		print e
#		return False


def add_playable_track(offset):
	circ_pos = (app.now_playing['pos']+offset)%playlist.size()
	print "Fetching track "+str(circ_pos+1)
	tid = app.now_playing['item']['tracks'][circ_pos]['trackId']
	tname = playlist.__getitem__(circ_pos).getfilename()
	playurl = api.get_playable_url(tid, mem.access_token)
	playlist.remove(tname)
	li = xbmcgui.ListItem(
            app.now_playing['item']["tracks"][circ_pos]["name"],
            path=app.now_playing['item']["tracks"][circ_pos]["previewURL"],
            iconImage=app.album_art_path+app.now_playing['item']["thumb"],
            thumbnailImage=app.album_art_path+app.now_playing['item']["thumb"]
			)
	info = {
            "title": app.now_playing['item']["tracks"][circ_pos]["name"],
            "album": app.now_playing['item']["album"],
            "artist": app.now_playing['item']["artist"],
            "duration": app.now_playing['item']["tracks"][circ_pos]["playbackSeconds"],
            "tracknumber": int(app.now_playing['item']["tracks"][circ_pos]["trackIndex"]),
			}
	li.setInfo("music", info)
	playlist.add(playurl, listitem=li, index=circ_pos)
	#print "Replaced dummy list item with real track info"


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


def verify_image_dir(ext):
	img_dir = __addon_path__+'/resources/skins/Default/media/album/'+ext
	if not os.path.isdir(img_dir):
		os.mkdir(img_dir)
		print ("Created the missing album image directory at " + img_dir)

	#else:
	#	print "Image directory is present!"
	return img_dir




#def remove_html_markup(s):
#	tag = False
#	quote = False
#	out = ""
#	for c in s:
#		if c == '<' and not quote:
#			tag = True
#		elif c == '>' and not quote:
#			tag = False
#		elif (c == '"' or c == "'") and tag:
#			quote = not quote
#		elif not tag:
#			out = out + c
#	out = out.replace("\n", " ")
#	return out



app = Application()
mem = Member()
alb = Album()
genres = Genres()
player = Player()
playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
api = rhapapi.Api()


app.set_var("BASEURL", "http://api.rhapsody.com/v1/")
app.set_var("S_BASEURL", "https://api.rhapsody.com/v1/")
app.set_var("AUTHURL", "https://api.rhapsody.com/oauth/token")
app.set_var("APIKEY",  "22Q1bFiwGxYA2eaG4vVAGsJqi3SQWzmd")
app.set_var("SECRET",  "Z1AAYBC1JEtnMJGm")
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
	print "Saved album data to cachefile"
del loadwin
gc.collect()
print "App has been exited"


