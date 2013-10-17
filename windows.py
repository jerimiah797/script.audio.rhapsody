__author__ = 'jham'


class LoginBase(xbmcgui.WindowXML):
	def __init__(self, xmlName, thescriptPath, defaultname, forceFallback):
		print "I'm the base login win class"


class LoginWin(LoginBase):
	def __init__(self, *args, **kwargs):
		LoginBase.__init__(self, *args)
		#self.mem = kwargs.get('member')


	def onInit(self):
		print "Starting onInit Loop"
		while not mem.logged_in:
			if mem.bad_creds:
				self.getControl(10).setLabel('Login failed! Try again...')
				print "Set fail label message"
			self.inputwin = InputDialog()
			self.inputwin.showInputDialog()
			mem.login_member(self.inputwin.name_txt, self.inputwin.pswd_txt)
			del self.inputwin
			print "Logged_in value: " + str(mem.logged_in)
			print "Bad Creds value: " + str(mem.bad_creds)

		print "Exited the while loop! Calling the del function"
		self.close()


class InputDialog(xbmcgui.WindowDialog):
	def __init__(self):
		img = __addon_path__+"/resources/skins/Default/media/textboxselected.png"
		print "path to image is: "+img
		self.name = xbmcgui.ControlEdit(530, 320, 400, 120, '', 'rhapsody_font16', '0xDD171717', focusTexture="none.png")
		self.addControl(self.name)
		#self.inputbox_username.setText("Here's some sample text")
		self.pswd = xbmcgui.ControlEdit(530, 320, 400, 120, '', font='rhapsody_font16', textColor='0xDD171717', focusTexture="none.png", isPassword=1)
		self.addControl(self.pswd)
		#self.inputbox_password.setText("Here's the password field")
		self.butn = xbmcgui.ControlButton(900, 480, 130, 50, 'Sign In', font='rhapsody_font24_title', textColor='0xDD171717',
		                                  focusedColor='0xDD171717', focusTexture="none.png")
		self.addControl(self.butn)
		self.setFocus(self.name)
		self.name_txt = ""
		self.pswd_txt = ""

	def onAction(self, action):
		print str(action.getId())
		print type(action)
		if action.getId() == 7:
			if self.getFocus() == self.name:
				self.setFocus(self.pswd)
			elif self.getFocus() == self.pswd:
				self.setFocus(self.butn)
			else: pass
		elif action.getId() == 18:
			if self.getFocus() == self.name:
				self.setFocus(self.pswd)
			elif self.getFocus() == self.pswd:
				self.setFocus(self.butn)
			else: pass
		else:
			pass


	def onControl(self, control):
		if control == self.butn:
			#print "if condition met: control == self.butn"
			#print "closing dialog window"
			self.close()
			self.name_txt = self.name.getText()
			self.pswd_txt = self.pswd.getText()
			#print self.name_txt
			#print self.pswd_txt
			count = 1
			return count
		else: pass


	def showInputDialog(self):
		self.name.setPosition(600, 320)
		self.name.setWidth(400)
		self.name.controlDown(self.pswd)
		self.pswd.setPosition(600, 410)
		self.pswd.setWidth(400)
		self.pswd.controlUp(self.name)
		self.pswd.controlDown(self.butn)
		self.butn.controlUp(self.pswd)
		self.doModal()


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
		print "Logged in? " + str(mem.logged_in)
		if not mem.logged_in:
			print "not already logged in. Checking for saved creds"
			if not mem.has_saved_creds():
				print "No saved creds. Need to do full login"
				self.logwin = LoginWin("login.xml", __addon_path__, 'Default', '720p', member=mem)
				self.logwin.doModal()
				del self.logwin
				print "deleting logwin"
			else:
				self.main()
		else:
			self.main()


	def main(self):
		#running = True
		#while running:
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
		if action.getId() == 10:
			#app.save_album_data()
			self.close()
		elif action.getId() == 92:
			#app.save_album_data()
			#xbmc.executebuiltin("ActivateWindow(yesnodialog)")
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
		print str(action.getId())
		print type(action)
		# --- Enter / Select ---
		if action.getId() == 7:
			# ---Play Button ---
			if self.getFocusId() == 21:
				alb.get_album_playlist(self.current_list, self.pos, self)

				player.play(alb.playlist)
				self.setCurrentListPosition(alb.playlist.getposition())
				#print "---------------Started playlist from dialog play button. Current playlist position is: "+str(alb.playlist.getposition())
				#print "---------------Current window list position is: "+str(self.getCurrentListPosition())
				#print "---------------Current playlist album is: "+win.current_playlist_albumId
				#print "---------------Current dialog album is: "+self.current_list[self.pos]["album_id"]
				self.setFocusId(51)
			# --- Next Button---
			elif self.getFocusId() == 27:
				self.clearList()
				#print "self.pos before: "+str(self.pos)
				#print "Album_id before: "+self.current_list[self.pos]["album_id"]
				self.pos = (self.pos+1) % len(self.current_list)
				#print "self.pos after:  "+str(self.pos)
				#print "Album_id after: "+self.current_list[self.pos]["album_id"]
				#player.sync_current_list_pos()
				self.show_info()
			# --- Prev Button ---
			elif self.getFocusId() == 26:
				self.clearList()
				self.pos = (self.pos-1) % len(self.current_list)
				#player.sync_current_list_pos()
				self.show_info()
			# --- tracklist ---
			elif self.getFocusId() == 51:
				print "Clicked on track # "+str(self.getCurrentListPosition()+1)
				if win.current_playlist_albumId != self.current_list[self.pos]["album_id"]:
					alb.get_album_playlist(self.current_list, self.pos, self)
					print "updating playlist with selected album"
				player.playselected(self.getCurrentListPosition())
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
		print "current list length: "+str(len(self.current_list))
		print "current self.pos: "+str(self.pos)
		self.getControl(6).setLabel(self.current_list[self.pos]["style"])
		self.getControl(7).setImage(self.current_list[self.pos]["bigthumb"])
		self.getControl(8).setLabel(self.current_list[self.pos]["album_date"])
		if self.current_list[self.pos]["orig_date"]:
			self.getControl(9).setLabel("Original Release: " + self.current_list[self.pos]["orig_date"])
		self.getControl(10).setLabel(self.current_list[self.pos]["label"])
		self.getControl(11).setText(self.current_list[self.pos]["album"])
		self.getControl(13).setLabel(self.current_list[self.pos]["artist"])
		self.getControl(14).setText(self.current_list[self.pos]["review"])


