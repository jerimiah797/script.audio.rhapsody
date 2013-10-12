import xbmc
import xbmcgui
from rhapsody import *

BASEURL = "http://api.rhapsody.com/v1/"
AUTHURL = 'https://api.rhapsody.com/oauth/token'
APIKEY = "22Q1bFiwGxYA2eaG4vVAGsJqi3SQWzmd"
SECRET = "Z1AAYBC1JEtnMJGm"
APPROOT = xbmc.translatePath('special://skin')


class LoginBase(xbmcgui.WindowXML):
	def __init__(self, xmlName, thescriptPath, defaultname, forceFallback):
		print "I'm the base login win class"


class LoginWin(LoginBase):
	def __init__(self, *args, **kwargs):
		LoginBase.__init__(self, *args)
		self.mem = kwargs.get('member')


	def onInit(self):
		print "Starting onInit Loop"
		while not self.mem.logged_in:
			if self.mem.bad_creds:
				self.getControl(10).setLabel('Login failed! Try again...')
				print "Set fail label message"
			self.inputwin = InputDialog()
			self.inputwin.showInputDialog()
			self.mem.login_member(self.inputwin.name_txt, self.inputwin.pswd_txt)
			del self.inputwin
			print "Logged_in value: " + str(self.mem.logged_in)
			print "Bad Creds value: " + str(self.mem.bad_creds)

		print "Exited the while loop! Calling the del function"
		self.close()
		#del self.inputwin


class InputDialog(xbmcgui.WindowDialog):
	def __init__(self):
		self.name = xbmcgui.ControlEdit(530, 320, 400, 120, '', 'rhapsody_font16', '0xDD171717')
		self.addControl(self.name)
		#self.inputbox_username.setText("Here's some sample text")
		self.pswd = xbmcgui.ControlEdit(530, 320, 400, 120, '', font='rhapsody_font16', textColor='0xDD171717', isPassword=1)
		self.addControl(self.pswd)
		#self.inputbox_password.setText("Here's the password field")
		self.butn = xbmcgui.ControlButton(900, 480, 130, 50, 'Sign In', font='rhapsody_font24_title', textColor='0xDD171717',
		                                  focusedColor='0xDD171717')
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
		self.newreleases = []
		self.pos = ""
		self.view = ""
		self.script_path = APPROOT+"scripts/"
		self.mem = Member()
		self.alb = Album()
		self.genres = Genres()
		self.browse_list = ["Browse_newreleases","Browse_topalbums","Browse_topartists","Browse_toptracks"]
		print "Script path: " + self.script_path


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
		print "Logged in? " + str(self.mem.logged_in)
		if not self.mem.logged_in:
			print "not already logged in. Checking for saved creds"
			if not self.mem.has_saved_creds():
				print "No saved creds. Need to do full login"
				self.logwin = LoginWin("login.xml", self.script_path, 'Default', '720p', member=self.mem)
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
		self.win.setProperty("username", self.mem.username)
		self.win.setProperty("password", self.mem.password)
		self.win.setProperty("guid", self.mem.guid)
		self.win.setProperty("token", self.mem.access_token)
		#self.win.setProperty("account_type", mem.account_type)
		#self.win.setProperty("date_created", mem.date_created)
		self.win.setProperty("full_name", self.mem.first_name)
		self.win.setProperty("country", self.mem.catalog)
		self.win.setProperty("logged_in", "true")
		if self.view == "Browse_newreleases":
			print "self.view = "+self.view
			#self.clearList()
			self.getControl(300).setVisible(True)
			self.getControl(50).setVisible(True)
			self.alb.get_newreleases(self, self.mem)
		if self.view == "Browse_topalbums":
			#self.clearList()
			self.getControl(300).setVisible(True)
			self.getControl(50).setVisible(True)
			self.alb.get_topalbums(self, self.mem)


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
			pass
		elif action.getId() == 92:
			pass
		else:
			pass


	def onClick(self, control):
		print "onclick(): control %i" % control
		self.pos = self.getCurrentListPosition()
		if control == 50:
			#print "onClick(): clicked item " + str(self.pos) + ": " + self.newreleases[self.pos]["album"]
			#get_album_details(self.newreleases, self.pos)
			#get_large_art(self.newreleases, self.pos)
			#get_album_review(self.newreleases, self.pos)
			print "Opening album detail dialog"
			alb_dialog = AlbumDialog("album.xml", self.script_path, 'Default', '720p', current_list=self.newreleases,
			                         pos=self.pos, alb=self.alb, gen=self.genres)
			alb_dialog.setProperty("review", "has_review")
			alb_dialog.doModal()
			del alb_dialog
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
		self.alb = kwargs.get('alb')
		self.genres = kwargs.get('gen')
		self.img_dir = APPROOT+'/scripts/resources/skins/Default/media/'
		self.bottom_nav = ""
		self.myPlayer = xbmc.Player()
		self.myPlaylist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
		self.current_playlist_albumId = None



	def onInit(self):
		#self.win = xbmcgui.WindowDialog(xbmcgui.getCurrentWindowDialogId())
		self.clearList()
		#self.bottom_nav = self.getControl(35)
		#self.bottom_nav.setVisible(False)
		self.show_info()



	def show_info(self):
		self.populate_fields()
		self.alb.get_large_art(self.current_list, self.pos)
		self.populate_fields()
		self.alb.get_album_review(self.current_list, self.pos)
		print self.getProperty("review")
		self.populate_fields()
		self.alb.get_album_details(self.current_list, self.pos, self.genres)
		self.populate_fields()
		self.alb.get_album_tracklist(self.current_list, self.pos, self)
		#print "focus id: "+str(self.getFocusId())


	def onAction(self, action):
		print str(action.getId())
		print type(action)
		# --- Enter / Select ---
		if action.getId() == 7:
			# ---Play Button ---
			if self.getFocusId() == 21:
				self.alb.get_album_playlist(self.current_list, self.pos, self)
				self.myPlayer.play(self.alb.playlist)
				self.setFocusId(51)
			# --- Next Button---
			elif self.getFocusId() == 27:
				self.clearList()
				self.pos = (self.pos+1) % len(self.current_list)
				self.show_info()
			# --- Prev Button ---
			elif self.getFocusId() == 26:
				self.clearList()
				self.pos = (self.pos-1) % len(self.current_list)
				self.show_info()
			elif self.getFocusId() == 51:
				print "Clicked on track # "+str(self.getCurrentListPosition()+1)
				if self.current_playlist_albumId != self.current_list[self.pos]["album_id"]:
					self.alb.get_album_playlist(self.current_list, self.pos, self)
					print "updating playlist with selected album"
				self.myPlayer.playselected(self.getCurrentListPosition())
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




