import time
import pickle
import xbmcgui
from lib import rhapapi

class ContentList():
	#handle new releases, top albums, artist discography, library album list, etc.
	def __init__(self, *args):

		self.data = []
		self.liz = []
		self.built = False
		self.pos = 0
		self.timestamp = time.time()
		self.type = args[0]
		self.name = args[1]
		self.filename = args[2]
		self.app = args[3]
		self.win = self.app.win
		self.cache = self.app.cache
		self.img = self.app.img
		self.api = self.app.api
		self.raw = None
		print 'running init code for '+self.name

	def fresh(self):
		return True

	def make_active(self):
		if (self.app.get_var('last_rendered_list') == self.name) and self.win.getListSize()>2:
			print "Window already has that list in memory. Skipping list building"
			return
		print "ContentList: make active " +self.name
		print "current frame: "+self.win.getProperty('frame')
		print "current view: "+self.win.getProperty('browseview')
		print "Built: "+str(self.built)
		print "Fresh: "+str(self.fresh())
		if self.built and self.fresh():
			print "doing simple list building for mainwin"
			self.build_winlist()
		else:
			print "Doing full data fetch and list building for mainwin"
			self.build()
		self.app.set_var('last_rendered_list', self.name)
		#if self.name == 'toptracks':
		#	win.sync_playlist_pos()
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
			d = {'newreleases':   self.api.get_new_releases,
			     'topalbums':     self.api.get_top_albums,
			     'topartists':    self.api.get_top_artists,
			     'toptracks':     self.api.get_top_tracks,
			     'lib_albums':    self.api.get_library_albums,
			     'lib_artists':   self.api.get_library_artists,
			     #'lib_tracks':    api.get_library_artist_tracks,
			     #'lib_stations':  api.get_library_stations,
			     #'lib_favorites': api.get_library_favorites
			     }
			r = d[self.name]()
			#self.save_raw_data(r)
		#utils.prettyprint(r)
		return r

	def ingest_list(self, results):

		print "Ingest list. Type: "+self.type
		self.win.clearList()
		__ = {}

		d = {'album': self.cache.album,
			 'artist': self.cache.artist,
		     'track':  __,
		     'station': __}

		store = d[self.type]

		for i, item in enumerate(results):
			id = item['id']
			if self.type == 'album':
				infos = self.process_album(i, item)
				self.data.append(infos[self.type]['album_id'])
			elif self.type == 'artist':
				infos = self.process_artist(i, item)
				self.data.append(infos[self.type]['artist_id'])
			elif self.type == 'track':
				infos = self.process_track(i, item)
				self.data.append(infos[self.type])
			self.liz.append(infos['listitem'])
			self.add_lizitem_to_winlist(infos['listitem'])
			if not id in store:
				store[id] = infos[self.type]

		self.built = True
		#utils.prettyprint(self.data)
		self.cache.save_album_data()
		self.cache.save_artist_data()


	def process_album(self, count, item):
		data = {}
		thumb = self.img.handler(item["images"][0]["url"], 'small', 'album')
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

		if not id in self.cache.artist:
			if id == 'Art.0':
				print "detected artist 0 case!"
				url = None
				genre = ""
			else:
				url = self.img.identify_largest_image(item["id"], "artist")
				g_id = self.api.get_artist_genre(item["id"])
				genre = self.cache.genre_dict__[g_id]
		else:
			#print 'using cached thumb url for artist image'
			url = self.cache.artist[id]['thumb_url']
			#print 'using cached genre for artist'
			genre = self.cache.artist[id]['style']

		bigthumb = self.img.handler(url, 'large', 'artist')

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
		thumb = 'none.png'
		data['track'] = {'trackId': item["id"],
		         'name': item["name"],
		         'thumb': thumb,
		         #'thumb_url': item["images"][0]["url"],
		         'album': item['album']['name'],
		         'displayAlbumName': item['album']['name'],
		         'albumId': item['album']['id'],
		         'genre_id': item['genre']['id'],
		         'duration': item['duration'],
		         'playbackSeconds': item['duration'],
		         'style': '',
		         'artist': item["artist"]["name"],
		         'displayArtistName': item["artist"]["name"],
		         'artistId': item["artist"]["id"],
		         'previewURL': item['sample'],
		         'list_id': count,
		         'trackIndex': count+1}
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
		self.win.addItem(li)

	def build_winlist(self):
		print "ContentList: build_winlist"
		self.win.clearList()
		for i, item in enumerate(self.liz):
			self.win.addItem(self.liz[i])
			#xbmc.sleep(2)
		print "list position: "+ str(self.pos)

class WindowTrackList():
	def __init__(self):
		pass
	#handle albums, playlists, radio, queue, listening history

	def get_litems(self, cache, id):
		print "Tracklist: adding dummy tracks for gui list"
		src = cache[id]
		list = []
		for i, item in enumerate(src["tracks"]):
			newlistitem = xbmcgui.ListItem(path="http://dummyurl.org")
			newlistitem.setInfo('music', { 'tracknumber':   int(src["tracks"][i]["trackIndex"]),
			                               'title':         src["tracks"][i]["name"],
			                               'duration':      int(src["tracks"][i]["playbackSeconds"])
			                               })
			list.append(newlistitem)
		print "Showing "+str(i+1)+" tracks"
		return list
