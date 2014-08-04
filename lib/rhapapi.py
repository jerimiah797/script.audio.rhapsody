import xbmc
import urllib
import urllib2
import base64
import datetime
import time
import utils
import sys
if sys.version_info >=  (2, 7):
    import json as json
else:
    import simplejson as json




class Api():

	def __init__(self):
		self.BASEURL = "http://api.rhapsody.com/v1/"
		self.S_BASEURL = "https://api.rhapsody.com/v1/"
		self.APIKEY = "22Q1bFiwGxYA2eaG4vVAGsJqi3SQWzmd"
		self.token = None


	def __get_data_from_rhapsody(self, req, timeout):
		succeed = 0
		while succeed < 3:
			try:
				response = urllib2.urlopen(req, timeout=timeout)
				try:
					results = json.load(response)
					return results
				except:
					return True
					"print Inner 'try' failed. What now?"
			except urllib2.HTTPError, e:
				print "url: "+ str(req.get_full_url())
				print "------------------  Bad server response ----------------"
				print e.headers
				print e
				succeed += 1
			except urllib2.URLError, e:
				print "url: "+ str(req.get_full_url())
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
		encuser = base64.b64encode(username)
		encpass = base64.b64encode(password)
		url = "http://rhap-xbmc-auth.herokuapp.com/auth?user=%s&pass=%s" % (encuser, encpass)
		print url
		req = self.__build_req(url)
		results = self.__get_data_from_rhapsody(req, 20)
		if results:
			#print results
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
		#if session[1][1]:
		#	url = "%ssessions/%s" %(self.S_BASEURL, session[1][1])
		if 'id' in session:
			url = "%ssessions/%s" %(self.S_BASEURL, session[u'id'])
			req = self.__build_member_req(url)
			results = self.__get_data_from_rhapsody(req, 5)
			if results:
				return results
			else:
				print "Validate Session call timed out"
				return False
		else:
			print "No existing session to check. "
			pass

	def get_session(self):
		print "Rhapapi: Creating Playback Session"
		data = {}
		url = "%ssessions" %(self.S_BASEURL)
		req = self.__build_member_req(url)
		req.add_data(data)
		results = self.__get_data_from_rhapsody(req, 5)
		return results

	def get_account_info(self):
		print "Rhapapi: Getting Account Details"
		data = {}
		url = "%sme/account" %(self.S_BASEURL)
		req = self.__build_member_req(url)
		#req.add_data(data)
		results = self.__get_data_from_rhapsody(req, 5)
		return results

	def log_playstart(self, track_id):
		print "Rhapapi: logging playstart notification"
		ztime = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
		url = "%sevents" %(self.S_BASEURL)
		data = {"type": "playbackStart", "client": "xbmc_internal", "playback": { "id": track_id, "started": ztime, "format": "AAC", "bitrate": 192 } }
		data = json.dumps(data)
		req = self.__build_member_req(url)
		req.add_header('Content-Type', 'application/json')
		req.add_data(data)
		results = self.__get_data_from_rhapsody(req, 5)
		print "Logging a Play Start event. "+str(results)
		return ztime


	def log_playstop(self, track_id, ztime, duration):
		print "Rhapapi: logging playstop notification"
		url = "%sevents" %(self.S_BASEURL)
		data = {"type": "playbackStop", "duration": duration, "client": "xbmc_internal", "playback": { "id": track_id, "started": ztime, "format": "AAC", "bitrate": 192 } }
		data = json.dumps(data)
		req = self.__build_member_req(url)
		req.add_header('Content-Type', 'application/json')
		req.add_data(data)
		results = self.__get_data_from_rhapsody(req, 5)
		return results


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
			#utils.prettyprint(results)
			return results
		else:
			return False


#------Listening History -----------

	def get_listening_history(self):
		print "Rhapapi: getting listening history tracks"
		url = "%sme/listens?apikey=%s" % (self.S_BASEURL, self.APIKEY)
		req = self.__build_member_req(url)
		results = self.__get_data_from_rhapsody(req, 20)
		if results:
			#utils.prettyprint(results)
			return results
		else:
			return False


#------------Playlists-------------------

	def get_library_playlists(self):
		print "Rhapapi: getting member playlists"
		url = "%sme/playlists" %(self.S_BASEURL)
		req = self.__build_member_req(url)
		results = self.__get_data_from_rhapsody(req, 20)
		if results:
			return results
		else:
			return False

	def get_playlist_details(self, plist_id):
		print "Rhapapi: getting playlist details"
		url = "%sme/playlists/%s/tracks" %(self.S_BASEURL, plist_id)
		req = self.__build_member_req(url)
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
			try:
				return results["genre"]["id"]
			except:
				print "Exception thrown getting genre id for "+artist_id


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

