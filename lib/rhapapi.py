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
		self.token = None


	def __get_data_from_rhapsody(self, req, timeout):
		succeed = 0
		while succeed < 2:
			#print "Rhapapi: trying to get data..."
			#print "timeout = "+str(timeout)
			try:
				response = urllib2.urlopen(req, timeout=timeout)
				results = json.load(response)
				#print "Rhapapi: received data from servers!"
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

	def __post_data_to_rhapsody(self, req, timeout):
		data = ""
		succeed = 0
		while succeed < 2:
			#print "Rhapapi: trying to get data..."
			#print "timeout = "+str(timeout)
			try:
				response = urllib2.urlopen(req, timeout=timeout, data=data)
				results = json.load(response)
				#print "Rhapapi: received data from servers!"
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

	def __build_member_req(self, url):
		#print "access token: "+self.token
		header = b'Bearer ' + self.token
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


	def get_playable_url(self, track_id):
		print "Rhapapi: getting playable url"
		url = "%splay/%s" %(self.S_BASEURL, track_id)
		req = self.__build_member_req(url)
		results = self.__get_data_from_rhapsody(req, 5)
		if not results:
			return False
		if results['url'][:5] == u'undef':
			return False
		else:
			return results['url']


	def validate_session(self, session):
		print "Rhapapi: Validating Playback Session"
		print session[u'id']
		url = "%ssessions/%s" %(self.S_BASEURL, session[u'id'])
		req = self.__build_member_req(url)
		results = self.__get_data_from_rhapsody(req, 20)
		if results:
			print results
			return results
		else:
			return False

	def get_session(self):
		print "Rhapapi: Creating Playback Session"
		url = "%ssessions" %(self.S_BASEURL)
		req = self.__build_member_req(url)
		results = self.__post_data_to_rhapsody(req, 5)
		print results
		return results

	def log_playstart(self):
		print "logging playstart notification"

	def log_playstop(self):
		print "logging playstop notification"

	#------Library -----------
	def get_library_albums(self):
		print "Rhapapi: getting library albums"
		url = "%sme/library/albums" %(self.S_BASEURL)
		req = self.__build_member_req(url)
		results = self.__get_data_from_rhapsody(req, 20)
		if results:
			return results
		else:
			return False

	def get_library_artists(self):
		print "Rhapapi: getting library artists"
		url = "%sme/library/artists" % (self.S_BASEURL)
		req = self.__build_member_req(url)
		results = self.__get_data_from_rhapsody(req, 20)
		if results:
			return results
		else:
			return False

	def get_library_artist_tracks(self, art_id):
		print "Rhapapi: getting library tracks"
		url = "%sme/library/artists/%s/tracks" % (self.S_BASEURL, art_id)
		req = self.__build_member_req(url)
		results = self.__get_data_from_rhapsody(req, 20)
		if results:
			utils.prettyprint(results)
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

	def get_artist_images(self, artist_id):
		print "Rhapapi: getting artist image"
		url = "%sartists/%s/images?apikey=%s" %(self.BASEURL, artist_id, self.APIKEY)
		req = self.__build_req(url)
		results = self.__get_data_from_rhapsody(req, 3)
		if results:
			return results
		else:
			return False

	def get_artist_genre(self, artist_id):
		print "Rhapapi: getting artist genre"
		url = "%sartists/%s?apikey=%s" %(self.BASEURL, artist_id, self.APIKEY)
		req = self.__build_req(url)
		results = self.__get_data_from_rhapsody(req, 3)
		if results:
			return results["genre"]["id"]
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
		#container = []
		if results:
			#d = {'id': 'playlist', 'tracks': results2}
			#container.append(d)
			#return container
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

