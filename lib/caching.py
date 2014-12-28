import pickle
import time
import os
from rhapapi import Api

class Cache(object):

	def __init__(self, app):
		self.app = app
		self.__addon_path__ = self.app.__addon_data__
		self.user_data = {} #object to store cached data

		self.genre_tree__ = []  #json data from rhapsody
		self.genre_dict__ = {}  #object to store cached data

		self.artist = {}  #object to store cached data                                convert to self-managing data class instance
		self.artist_file = os.path.join(self.__addon_path__, '.artistdb.obj')  #picklefile

		self.album = {}  #object to store cached data
		self.album_file = os.path.join(self.__addon_path__, '.albumdb.obj')  #picklefile

		self.playlist = {}  #object to store cached data
		self.playlist_file = os.path.join(self.__addon_path__, '.playlistdb.obj') #picklefile

		self.genre = {}  #object to store cached data
		self.genre_file = os.path.join(self.__addon_path__, '.genres.obj')  #picklefile
		self.genre_modified = False

		self.api = self.app.api

	def save_genre_data(self):
		t1 = time.time()
		self.genre['genretree'] = self.genre_tree__
		self.genre['genredict'] = self.genre_dict__
		self.genre['timestamp'] = time.time()
		jar = open(self.genre_file, 'wb')
		pickle.dump(self.genre, jar)
		jar.close()
		t2 = time.time()
		print "Genre data saved!  Operation took "+str(t2-t1)


	def save_album_data(self):
		t1 = time.time()
		jar = open(self.album_file, 'wb')
		pickle.dump(self.album, jar)
		jar.close()
		t2 = time.time()
		print "Album info saved in cachefile! Operation took "+str(t2-t1)


	def save_artist_data(self):
		t1 = time.time()
		jar = open(self.artist_file, 'wb')
		pickle.dump(self.artist, jar)
		jar.close()
		t2 = time.time()
		print "Artist info saved in cachefile! Operation took "+str(t2-t1)


	def load_cached_data(self):
		print "checking cached data"
		try:
			pkl_file = open(self.album_file, 'rb')
			self.album = pickle.load(pkl_file)
			pkl_file.close()
			print "Loaded Album cache"
		except:
			print "Couldn't find album cache on disk. "

		try:
			pkl_file = open(self.artist_file, 'rb')
			self.artist = pickle.load(pkl_file)
			pkl_file.close()
			print "Loaded Artist cache"
		except:
			print "Couldn't find artist cache on disk."

		try:
			pkl_file = open(self.genre_file, 'rb')
			self.genre = pickle.load(pkl_file)
			pkl_file.close()
			self.genre_tree__ = self.genre['genretree']
			self.genre_dict__ = self.genre['genredict']
			print "Loaded genre cache from disk."
		except:
			print("Couldn't find genre cache on disk. Regenerating...")
			self.get_genre_tree()
			self.flatten_genre_keys(self.genre_tree__)
			self.save_genre_data()

	def get_genre_tree(self):
		results = self.api.get_genres()
		if results:
			self.genre_tree__ = results
		else:
			print "Couldn't retrieve genre list from server!"

	def flatten_genre_keys(self, j):
		for item in j:
			self.genre_dict__[item['id']] = item['name']
			#print "added a key for "+item['name']
			if 'subgenres' in item:
				#print "found subgenres. Calling self recursively"
				self.flatten_genre_keys(item['subgenres'])

