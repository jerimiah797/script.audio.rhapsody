import urllib
import os
#import rhapapi

class Image(object):

	def __init__(self, media_path, data_path, app):
		self.base_path = data_path
		self.media_path = os.path.join(media_path, "resources", "skins", "Default", "media")
		print "media path: "+self.media_path
		self.album_small_path =  "album"
		self.album_large_path = "large"
		self.artist_small_path = "artist"
		self.artist_large_path = "large"
		self.default_album_img = os.path.join(self.media_path, "AlbumPlaceholder.png")
		self.default_artist_img = os.path.join(self.media_path, "ArtistPlaceholder.png")
		self.verify_image_dirs()
		self.api = app.api
		pass

	def download_image(self, url, path):
		try:
			#print "Download Image: downloading "+url+" to "+path
			urllib.urlretrieve(url, path)
		except:
			#print "image download failed. URL: "+url+" Path: "+path
			pass


	def verify_image_dirs(self):
		dirs = [os.path.join(self.base_path, self.album_small_path),
		        os.path.join(self.base_path, self.album_small_path, self.album_large_path),
		        os.path.join(self.base_path, self.artist_small_path),
		        os.path.join(self.base_path, self.artist_small_path, self.artist_large_path)]
		for path in dirs:
			if not os.path.isdir(path):
				os.mkdir(path)
				print "created image directory at "+path
			else:
				print "verified image directory at "+path


	def handler(self, url, size, kind):
		if not url:
			#print "no image to download. Using default image."
			return self.default_album_img
		else:
			prefix_path = self.get_prefix_path(size, kind)
			#print "Prefix path: "+prefix_path
			img_filename = url.split('/')[(len(url.split('/'))) - 1]
			#print "Handling "+prefix_path+img_filename
			full_path = os.path.join(self.base_path, prefix_path, img_filename)
			if not os.path.isfile(full_path):
				self.download_image(url, full_path)
				#print "image handler: downloaded "+prefix_path+img_filename
			return os.path.join(prefix_path, img_filename)


	def identify_largest_image(self, id, kind):
		results = None
		#api = rhapapi.Api()
		if kind == "album":
			results = self.api.get_album_images(id)
		elif kind == "artist":
			results = self.api.get_artist_images(id)
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

	def identify_artist_thumb(self, id):
		results = None
		#api = rhapapi.Api()
		results = self.api.get_artist_images(id)
		if results:
			url = results[0]["url"]
			#print "IMG.identify_artist_thumb - found artist image url: "+str(url)
			return url
		


	def get_prefix_path(self, size, kind):

		d = {"album": {"small": self.album_small_path,
		               "large": os.path.join(self.album_small_path, self.album_large_path)},
			"artist": {"small": self.artist_small_path,
			           "large": os.path.join(self.artist_small_path, self.artist_large_path)}
			}

		return d[kind][size]

