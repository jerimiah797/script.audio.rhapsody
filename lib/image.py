import urllib
import os

class Images():

	def __init__(self, path):
		self.base_path = path+"/resources/skins/Default/media/"
		self.album_small_path = self.base_path+"album/"
		self.album_large_path = self.base_path+"album/large/"
		self.artist_small_path = self.base_path+"artist/"
		self.artist_large_path = self.base_path+"artist/large"
		self.default_album_img = self.base_path+"AlbumPlaceholder.png"
		self.verify_image_dirs()
		pass

	def download_image(self, url, path):
		try:
			urllib.urlretrieve(url, path)
		except:
			print "image download failed"


	def verify_image_dirs(self):
		dirs = [self.album_small_path, self.album_large_path, self.artist_small_path, self.artist_large_path]
		print "Verifying all image directories"
		for path in dirs:
			if not os.path.isdir(path):
				os.mkdir(path)
				print "created image directory at "+path