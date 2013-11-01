import urllib
import os
import rhapapi

class Image():

	def __init__(self, path):
		self.base_path = path+"/resources/skins/Default/media/"
		self.album_small_path = "album/"
		self.album_large_path = "album/large/"
		self.artist_small_path = "artist/"
		self.artist_large_path = "artist/large"
		self.default_album_img = self.base_path+"AlbumPlaceholder.png"
		self.verify_image_dirs()
		pass

	def download_image(self, url, path):
		try:
			urllib.urlretrieve(url, path)
		except:
			print "image download failed"


	def verify_image_dirs(self):
		dirs = [self.base_path+self.album_small_path,
		        self.base_path+self.album_large_path,
		        self.base_path+self.artist_small_path,
		        self.base_path+self.artist_large_path]
		for path in dirs:
			if not os.path.isdir(path):
				os.mkdir(path)
				print "created image directory at "+path


	def handler(self, url, size, kind):
		prefix_path = self.get_prefix_path(size, kind)
		img_filename = url.split('/')[(len(url.split('/'))) - 1]
		#print "Handling "+prefix_path+img_filename
		full_path = self.base_path+prefix_path+img_filename
		if not os.path.isfile(full_path):
			self.download_image(url, full_path)
			print "downloaded "+prefix_path+img_filename
		return prefix_path+img_filename


	def identify_largest_image(self, album_id):
		api = rhapapi.Api()
		results = api.get_album_images(album_id)
		if results:
			biggest = 0
			biggest_index = 0
			for y in xrange(0, len(results)):
				s = results[y]["width"]
				if (s > biggest):
					biggest = s
					biggest_index = y
			url = results[biggest_index]["url"]
			#print "identified biggest image as: "+url
			return url


	def get_prefix_path(self, size, kind):
		if kind == "album":
			if size == "small":
				return self.album_small_path
			if size == "large":
				return self.album_large_path
		if kind == "artist":
			if size == "small":
				return self.artist_small_path
			if size == "large":
				return self.artist_large_path