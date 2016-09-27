import xbmcaddon
import xbmc
import xbmcgui
import xbmcvfs
from lib import rhapapi
from lib import image
from lib import member
from lib import play
from lib import views
from lib.views import view
from lib import lists
from lib import caching
from lib import MyFont
from lib import httpd
import sys
import os



class Application():
	__vars = None


	def __init__(self):
		print "Initializing Rhapsody for XBMC"
		self.__vars = {}  #dict for app vars
		self.view_keeper = {'browseview': 'browse_newreleases', 'frame': 'Browse', 'view_id':3350}

		self.__addon_id__ = 'script.audio.rhapsody'
		self.__addon_cfg__ = xbmcaddon.Addon(self.__addon_id__)
		self.__addon_path__ = self.__addon_cfg__.getAddonInfo('path')
		self.__addon_version__ = self.__addon_cfg__.getAddonInfo('version')
		self.__addon_icon__ = self.__addon_cfg__.getAddonInfo('icon')
		self.__addon_data__ = os.path.join(xbmc.translatePath('special://userdata/addon_data/'), self.__addon_id__)

		self.init_dirs()

		self.newreleases =     None
		self.topalbums =       None
		self.topartists =      None
		self.toptracks =       None
		self.lib_albums =      None
		self.lib_artists =     None
		self.hist_tracks =     None
		self.srch_albums =     None
		self.srch_artists =    None
		self.srch_tracks =     None
		self.srch_brdcst =     None
		self.windowtracklist = None

		self.player = None
		self.playlist = None

		self.mem = member.Member(self)
		self.api = rhapapi.Api(self)
		self.cache = caching.Cache(self)
		self.img = image.Image(self.__addon_path__, self.__addon_data__, self)
		self.win = view.MainWin("main.xml", self.__addon_path__, 'Default', '720p', app=self)
		self.srv = httpd.TinyWebServer(self)

		self.srv.create("localhost", 8090)
		self.srv.start()

		self.wait = False

		
		self.init_lists()
		self.init_vars()

		self.player = play.Player(xbmc.PLAYER_CORE_AUTO, app=self)
		self.playlist = self.player.playlist
		#self.win.toptracks = self.toptracks
		self.win.player = self.player
		self.win.playlist = self.playlist

		self.loadwin = xbmcgui.WindowXML("loading.xml", self.__addon_path__, 'Default', '720p')
		self.loadwin.show()

	def init_dirs(self):
		if not xbmcvfs.exists(self.__addon_data__):
			xbmcvfs.mkdir(self.__addon_data__)
			print "Created addon data folder"
		else:
			print "Found existing addon data folder"


	def init_lists(self):
		self.newreleases =   lists.ContentList('album',   'newreleases',   self.__addon_data__+'/.newreleases.obj',   self)
		self.topalbums =     lists.ContentList('album',   'topalbums',     self.__addon_data__+'/.topalbums.obj',     self)
		self.topartists =    lists.ContentList('artist',  'topartists',    self.__addon_data__+'/.topartists.obj',    self)
		self.toptracks =     lists.ContentList('track',   'toptracks',     self.__addon_data__+'/.toptracks.obj',     self)
		self.lib_albums =    lists.ContentList('album',   'lib_albums',    self.__addon_data__+'/.lib_albums.obj',    self)
		self.lib_artists =   lists.ContentList('artist',  'lib_artists',   self.__addon_data__+'/.lib_artists.obj',   self)
		self.hist_tracks =   lists.ContentList('track',   'hist_tracks',   self.__addon_data__+'/.hist_tracks.obj',   self)
		self.lib_playlists = lists.ContentList('playlist','lib_playlists', self.__addon_data__+'/.lib_playlists.obj', self)
		self.srch_albums =   lists.ContentList('album',   'srch_albums',   self.__addon_data__+'/.srch_albums.obj',   self)
		self.srch_artists =  lists.ContentList('artist',  'srch_artists',  self.__addon_data__+'/.srch_artists.obj',  self)
		self.srch_tracks =   lists.ContentList('track',   'srch_tracks',   self.__addon_data__+'/.srch_tracks.obj',   self)
		self.srch_brdcst =   lists.ContentList('brdcst',  'srch_brdcst',   self.__addon_data__+'/.srch_brdcst.obj',   self)
		#lib_tracks =    ContentList('track',   'lib_tracks',    __addon_data__+'.lib_tracks.obj')
		#lib_stations =  ContentList('station', 'lib_stations',  __addon_data__+'.lib_stations.obj')
		#lib_favorites = ContentList('tracks',  'lib_favorites', __addon_data__+'.lib_favorites.obj')
		self.windowtracklist = lists.WindowTrackList()

	def reinit_lists(self):
		print "Reinitializing library lists"
		self.win.clist = self.win.getControl(3550) #delete library album list cached in window control
		self.win.clist.reset()
		self.win.clist = self.win.getControl(3551) #delete library artist list cached in window control
		self.win.clist.reset()
		self.lib_albums.fresh = False
		self.lib_artists.fresh = False
		self.hist_tracks.fresh = False
		self.lib_playlists.fresh = False

	def init_vars(self):
		self.set_var('view_matrix' , {"browse_newreleases":   self.newreleases,
						               "browse_topalbums":   self.topalbums,
						               "browse_topartists":  self.topartists,
						               "browse_toptracks":   self.toptracks,
						               "search_albums":	     self.srch_albums,
						               "search_artists":     self.srch_artists,
						               "search_tracks":      self.srch_tracks,
						               "search_broadcast":   self.srch_brdcst,
						               "library_albums":     self.lib_albums,
						               "library_artists":    self.lib_artists,
		                               "history_tracks":     self.hist_tracks,
		                               "library_playlists":  self.lib_playlists,
						               #"library_tracks":     lib_tracks,
						               #"library_stations":   lib_stations,
						               #"library_favorites":  lib_favorites,
						               })

		self.set_var('list_matrix' , {"browse_newreleases":		3350,
						              "browse_topalbums":     	3351,
						              "browse_topartists":    	3352,
						              "browse_toptracks":     	3353,
						              "search_albums":		  	3451,
						              "search_artists":			3452,
						              "search_tracks":			3453,
						              "search_broadcast":		3454,
						              "library_albums":       	3550,
						              "library_artists":      	3551,
		                              "history_tracks":       	3950,
		                              "library_playlists":    	3650
						                })

		self.set_var('running', True)
		self.set_var('logged_in', False)
		self.set_var('bad_creds', False)
		self.set_var('last_rendered_list', None)
		self.set_var('exiting', False)
		#self.set_var('alb_dialog_id', None)

	def init_fonts(self):
		print "Installing Rhapsody fonts"
		MyFont.addFont( "rhapsody_font8" , "segoeuisl.ttf" , "10", self.__addon_path__ )
		MyFont.addFont( "rhapsody_font9" , "segoeuisl.ttf" , "12", self.__addon_path__  )
		MyFont.addFont( "rhapsody_font10" , "segoeuisl.ttf" , "14", self.__addon_path__  )
		MyFont.addFont( "rhapsody_font12" , "segoeuisl.ttf" , "17", self.__addon_path__  )
		MyFont.addFont( "rhapsody_font13" , "segoeuisl.ttf" , "20", self.__addon_path__  )
		MyFont.addFont( "rhapsody_font14" , "segoeuisl.ttf" , "22", self.__addon_path__  )
		MyFont.addFont( "rhapsody_font16" , "segoeuisl.ttf" , "25", self.__addon_path__  )
		MyFont.addFont( "rhapsody_font30" , "segoeuisl.ttf" , "30", self.__addon_path__  )
		MyFont.addFont( "rhapsody_fontContextMenu" , "segoeuisl.ttf" , "18", self.__addon_path__  )

		MyFont.addFont( "rhapsody_font10_title" , "seguisb.ttf" , "12", self.__addon_path__  )
		MyFont.addFont( "rhapsody_font12_title" , "seguisb.ttf" , "17", self.__addon_path__  )
		MyFont.addFont( "rhapsody_font13_title" , "seguisb.ttf" , "20", self.__addon_path__  )
		MyFont.addFont( "rhapsody_font24_title" , "seguisb.ttf" , "24", self.__addon_path__  )
		MyFont.addFont( "rhapsody_font28_title" , "seguisb.ttf" , "28", self.__addon_path__  )
		MyFont.addFont( "rhapsody_font30_title" , "seguisb.ttf" , "30", self.__addon_path__  )
		MyFont.addFont( "rhapsody_font35_title" , "seguisb.ttf" , "35", self.__addon_path__  )
		MyFont.addFont( "rhapsody_font45caps_title" , "seguisb.ttf" , "45", self.__addon_path__  )
		MyFont.addFont( "rhapsody_WeatherTemp" , "seguisb.ttf" , "80", self.__addon_path__  )

		MyFont.addFont( "rhapsody_symbol72" , "RhapsodySymbol.ttf" , "72", self.__addon_path__  )
		MyFont.addFont( "rhapsody_symbol96" , "RhapsodySymbol.ttf" , "96", self.__addon_path__  )
		MyFont.addFont( "rhapsody_symbol144" , "RhapsodySymbol.ttf" , "144", self.__addon_path__  )




	def set_var(self, name, value):
		self.__vars[name] = value


	def has_var(self, name):
		return name in self.__vars


	def get_var(self, name):
		return self.__vars[name]


	def remove_var(self, name):
		del self.__vars[name]

