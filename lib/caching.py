import pickle
import time
from rhapapi import Api

class Cache():

	def __init__(self, *args):
		__addon_path__ = args[0]
		self.user_data = {} #object to store cached data

		self.genre_tree__ = []  #json data from rhapsody
		self.genre_dict__ = {}  #object to store cached data

		self.artist = {}  #object to store cached data                                convert to self-managing data class instance
		self.artist_file = __addon_path__+'/resources/.artistdb.obj'  #picklefile

		self.album = {}  #object to store cached data
		self.album_file = __addon_path__+'/resources/.albumdb.obj'  #picklefile

		self.genre = {}  #object to store cached data
		self.genre_file = __addon_path__+'/resources/.genres.obj'  #picklefile

		self.api = Api()

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
			self.get_genre_tree()
			self.flatten_genre_keys(self.genre_tree__)
			self.save_genre_data()

	def get_genre_tree(self):
		results = self.api.get_genres()
		if results:
			self.genre_tree__ = results
		else:
			print "Couldn't retrieve genres!"

	def flatten_genre_keys(self, j):
		for item in j:
			self.genre_dict__[item['id']] = item['name']
			#print "added a key for "+item['name']
			if 'subgenres' in item:
				#print "found subgenres. Calling self recursively"
				self.flatten_genre_keys(item['subgenres'])