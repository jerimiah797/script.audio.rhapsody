import xbmc
import urllib
import urllib2
import json
import base64
import utils



class Api():

	def __init__(self):
		self.BASEURL = "http://api.rhapsody.com/v1/"
		self.S_BASEURL = "https://api.rhapsody.com/v1/"
		self.AUTHURL = "https://api.rhapsody.com/oauth/token"
		self.APIKEY = "22Q1bFiwGxYA2eaG4vVAGsJqi3SQWzmd"
		self.SECRET = "Z1AAYBC1JEtnMJGm"


	def __get_data_from_rhapsody(self, req, timeout):
		succeed = 0
		while succeed < 2:
			print "Rhapapi: trying to get data..."
			try:
				response = urllib2.urlopen(req, timeout=timeout)
				results = json.load(response)
				print "Rhapapi: received data from servers!"
				return results
			except urllib2.HTTPError, e:
				print "------------------  Bad server response ----------------"
				print e.headers
				print e
				#xbmc.sleep(1000)
				succeed += 1
			except urllib2.URLError, e:
				print 'We failed to reach a server.'
				print 'Reason: ', e.reason
				succeed += 1
		return False


#----------- Secure API calls requiring auth headers ---------

	def __build_member_req(self, url, access_token):
		header = b'Bearer ' + access_token
		req = urllib2.Request(url)
		req.add_header('Authorization', header)
		return req

	def __build_req(self, url):
		req = urllib2.Request(url)
		return req


	def login_member(self, username, password):
		print "Rhapapi: getting access token"
		data = urllib.urlencode({'username': username, 'password': password, 'grant_type': 'password'})
		header = b'Basic ' + base64.b64encode(self.APIKEY + b':' + self.SECRET)
		req = urllib2.Request(self.AUTHURL, data)
		req.add_header('Authorization', header)
		results = self.__get_data_from_rhapsody(req, 5)
		if results:
			return results
		else:
			return False


	def get_playable_url(self, track_id, access_token):
		print "Rhapapi: getting playable url"
		url = "%splay/%s" %(self.S_BASEURL, track_id)
		req = self.__build_member_req(url, access_token)
		results = self.__get_data_from_rhapsody(req, 5)
		if results:
			return results['url']
		else:
			return False

	def validate_session(self):
		pass

	def get_session(self):
		pass

	def log_playstart(self):
		pass

	def log_playstop(self):
		pass

	#------Library -----------
	def get_library_albums(self, access_token):
		print "Rhapapi: getting library albums"
		url = "https://api.rhapsody.com/v1/me/library/albums"
		req = self.__build_member_req(url, access_token)
		results = self.__get_data_from_rhapsody(req, 20)
		if results:
			return results
		else:
			return False


#----------- Normal API calls  ---------

	def get_album_review(self, album_id):
		print "Rhapapi: getting album review"
		url = "%salbums/%s/reviews?apikey=%s" % (self.BASEURL, album_id, self.APIKEY)
		req = self.__build_req(url)
		results = self.__get_data_from_rhapsody(req, 3)
		if results:
			return utils.remove_html_markup(results[0]["body"])
		else:
			return False

	def get_album_details(self, album_id):
		print "Rhapapi: getting album details"
		#url = '%salbums/new?apikey=%s&limit=100' % (self.BASEURL, self.APIKEY)
		url = "http://direct.rhapsody.com/metadata/data/methods/getAlbum.js?developerKey=9H9H9E6G1E4I5E0I&albumId=%s&cobrandId=40134&filterRightsKey=0" % (album_id)
		req = self.__build_req(url)
		results = self.__get_data_from_rhapsody(req, 3)
		if results:
			return results
		else:
			return False

	def get_album_images(self, album_id):
		print "Rhapapi: getting album image"
		url = "%salbums/%s/images?apikey=%s" %(self.BASEURL, album_id, self.APIKEY)
		req = self.__build_req(url)
		results = self.__get_data_from_rhapsody(req, 3)
		if results:
			return results
		else:
			return False


	def get_new_releases(self):
		print "Rhapapi: getting new releases"
		url = '%salbums/new?apikey=%s&limit=100' % (self.BASEURL, self.APIKEY)
		req = self.__build_req(url)
		results = self.__get_data_from_rhapsody(req, 3)
		if results:
			return results
		else:
			return False


	def get_top_albums(self):
		print "Rhapapi: getting top albums"
		url = '%salbums/top?apikey=%s&limit=100' % (self.BASEURL, self.APIKEY)
		req = self.__build_req(url)
		results = self.__get_data_from_rhapsody(req, 3)
		if results:
			return results
		else:
			return False

	def get_top_artists(self):
		print "Rhapapi: getting top artists"
		url = '%sartists/top?apikey=%s&limit=100' % (self.BASEURL, self.APIKEY)
		req = self.__build_req(url)
		results = self.__get_data_from_rhapsody(req, 3)
		if results:
			return results
		else:
			return False

	def get_top_tracks(self):
		print "Rhapapi: getting top tracks"
		url = '%stracks/top?apikey=%s&limit=100' % (self.BASEURL, self.APIKEY)
		req = self.__build_req(url)
		results = self.__get_data_from_rhapsody(req, 3)
		if results:
			return results
		else:
			return False

	def get_genres(self):
		print "Rhapapi: getting genres"
		url = "%sgenres?apikey=%s" % (self.BASEURL, self.APIKEY)
		req = self.__build_req(url)
		results = self.__get_data_from_rhapsody(req, 3)
		if results:
			return results
		else:
			return False


	def get_bio(self, art_id):
		print "Rhapapi: getting artist bio"
		url = "%sartists/%s/bio?apikey=%s" % (self.BASEURL, art_id, self.APIKEY)
		req = self.__build_req(url)
		results = self.__get_data_from_rhapsody(req, 3)
		if results:
			return utils.remove_html_markup(results['bio'])
		else:
			return False