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




class Api(object):

	def __init__(self, app):
		self.BASEURL = "http://api.rhapsody.com/v1/"
		self.S_BASEURL = "https://api.rhapsody.com/v1/"
		self.APIKEY = "22Q1bFiwGxYA2eaG4vVAGsJqi3SQWzmd"
		self.app = app



	def __get_data_from_rhapsody(self, req, timeout):
		succeed = 0
		localreq = req
		while succeed < 1:
			#print "succeed = "+str(succeed)
			try:
				#print "starting first try expression"
				t1 = time.time()				
				try:
					#print "starting second try expression"
					response = urllib2.urlopen(localreq, timeout=timeout)
					t2 = time.time()
					print "Call to %s succeeded in %s seconds" % (str(localreq.get_full_url()), '%.3f'%(t2-t1))
					try:
						results = json.load(response)
						#utils.prettyprint(results)
						return results
					except:
						return True
						#Some calls such as playstart and playstop succeed but return no data
				except urllib2.HTTPError, e:
					#print "url: "+ str(req.get_full_url())
					print "------------------  Bad server response ----------------"
					#print e.headers
					print e
					if succeed == 0:
						print "(inner) something went very wrong with that request. Let's try refreshing our token"
						self.login_member(self.app.mem.username, self.app.mem.password)
						localreq = self.__build_member_req(req.get_full_url())
						succeed += 1
					elif succeed == 1:
						print "that didn't work"
						return False
				except urllib2.URLError, e:
					#print "url: "+ str(req.get_full_url())
					print 'We failed to reach a server.'
					print 'Reason: ', e.reason
					succeed += 1
					xbmc.sleep(500)
					return False
				#return False
			except:
				print "(outer) something went very wrong with that request."
				#self.login_member(self.app.mem.username, self.app.mem.password)
				#localreq = self.__build_member_req(req.get_full_url())
				xbmc.sleep(1000)


#----------- Secure API calls requiring auth headers ---------

	def __build_member_req(self, url):
		#print "access token: "+self.app.mem.access_token
		#print "url: "+url
		header = b'Bearer ' + self.app.mem.access_token
		req = urllib2.Request(url)
		req.add_header('Authorization', header)
		return req
		

	def __build_req(self, url):
		req = urllib2.Request(url)
		return req


	def login_member(self, username, password):
		print "Rhapapi: Logging in member"
		#self.username = username
		#self.password = password
		encuser = base64.b64encode(username)
		encpass = base64.b64encode(password)
		url = "http://rhap-xbmc-auth.herokuapp.com/auth?user=%s&pass=%s" % (encuser, encpass)
		#print url
		req = self.__build_req(url)
		results = self.__get_data_from_rhapsody(req, 20)
		if results:
			self.app.mem.access_token = results["access_token"]
			#print "got a new access token: "+self.app.mem.access_token
			self.app.wait = False
			return results
		else:
			return False


	def get_playable_url(self, track_id):
		print "Rhapapi: getting playable url"
		#print track_id
		url = "%splay/%s" %(self.S_BASEURL, track_id)
		req = self.__build_member_req(url)
		results = self.__get_data_from_rhapsody(req, 2)
		if not results:
			return False
		if results['url'][:5] == u'undef':
			return False
		else:
			return results['url']


	def validate_session(self, session):
		print "Rhapapi: Validating Playback Session"
		if 'id' in session:
			url = "%ssessions/%s" %(self.S_BASEURL, session[u'id'])
			req = self.__build_member_req(url)
			results = self.__get_data_from_rhapsody(req, 30)
			if results:
				#utils.prettyprint(results)
				return results['valid']
			else:
				print "Validate Session call didn't work. This means it is expired, rather than invalid"
				results = None
				return results
		else:
			print "No existing session to check. "
			pass

	def get_session(self):
		print "Rhapapi: Creating Playback Session"
		data = {}
		url = "%ssessions" %(self.S_BASEURL)
		req = self.__build_member_req(url)
		req.add_data(data)
		results = self.__get_data_from_rhapsody(req, 10)
		return results

	def get_account_info(self):
		print "Rhapapi: Getting Account Details"
		data = {}
		url = "%sme/account" %(self.S_BASEURL)
		req = self.__build_member_req(url)
		#req.add_data(data)
		results = self.__get_data_from_rhapsody(req, 10)
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
		results = self.__get_data_from_rhapsody(req, 10)
		#print "Logging a Play Start event. "+str(results)
		return ztime


	def log_playstop(self, track_id, ztime, duration):
		print "Rhapapi: logging playstop notification"
		url = "%sevents" %(self.S_BASEURL)
		data = {"type": "playbackStop", "duration": duration, "client": "xbmc_internal", "playback": { "id": track_id, "started": ztime, "format": "AAC", "bitrate": 192 } }
		data = json.dumps(data)
		req = self.__build_member_req(url)
		req.add_header('Content-Type', 'application/json')
		req.add_data(data)
		results = self.__get_data_from_rhapsody(req, 10)
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

	def add_album_to_library(self, alb_id):
		print "Rhapapi: Add album %s to library" % (alb_id)
		data = {"id": alb_id}
		data = json.dumps(data)
		url = "%sme/library/albums" % (self.S_BASEURL)
		req = self.__build_member_req(url)
		req.add_header('Content-Type', 'application/json')
		req.add_data(data)
		results = self.__get_data_from_rhapsody(req, 5)
		if results:
			print "results:"
			utils.prettyprint(results)
			return True
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
		url = "%salbums/%s/reviews?apikey=%s&catalog=%s" % (self.BASEURL, album_id, self.APIKEY, self.app.mem.catalog)
		req = self.__build_req(url)
		results = self.__get_data_from_rhapsody(req, 10)
		if results:
			return utils.remove_html_markup(results[0]["body"])
		else:
			return False

	def get_album_details(self, album_id):
		print "Rhapapi: getting album details"
		url = '%salbums/%s?apikey=%s&catalog=%s' % (self.BASEURL, album_id, self.APIKEY, self.app.mem.catalog)
		#url = "http://direct.rhapsody.com/metadata/data/methods/getAlbum.js?developerKey=9H9H9E6G1E4I5E0I&albumId=%s&cobrandId=40134&filterRightsKey=0" % (album_id)
		req = self.__build_req(url)
		results = self.__get_data_from_rhapsody(req, 10)
		if results:
			#utils.prettyprint(results)
			return results
		else:
			return False

	def get_album_images(self, album_id):
		print "Rhapapi: getting album image"
		url = "%salbums/%s/images?apikey=%s&catalog=%s" %(self.BASEURL, album_id, self.APIKEY, self.app.mem.catalog)
		req = self.__build_req(url)
		results = self.__get_data_from_rhapsody(req, 10)
		if results:
			return results
		else:
			return False

	def get_artist_images(self, artist_id):
		print "Rhapapi: getting artist image"
		url = "%sartists/%s/images?apikey=%s&catalog=%s" %(self.BASEURL, artist_id, self.APIKEY, self.app.mem.catalog)
		req = self.__build_req(url)
		results = self.__get_data_from_rhapsody(req, 10)
		if results:
			return results
		else:
			return False

	def get_artist_genre(self, artist_id):
		print "Rhapapi: getting artist genre"
		url = "%sartists/%s?apikey=%s&catalog=%s" %(self.BASEURL, artist_id, self.APIKEY, self.app.mem.catalog)
		req = self.__build_req(url)
		results = self.__get_data_from_rhapsody(req, 10)
		if results:
			try:
				return results["genre"]["id"]
			except:
				print "Exception thrown getting genre id for "+artist_id

	def get_new_releases(self):
		print "Rhapapi: getting new releases"
		url = '%salbums/new?apikey=%s&limit=100&catalog=%s' % (self.BASEURL, self.APIKEY, self.app.mem.catalog)
		req = self.__build_req(url)
		results = self.__get_data_from_rhapsody(req, 10)
		if results:
			return results
		else:
			return False

	def get_top_albums(self):
		print "Rhapapi: getting top albums"
		url = '%salbums/top?apikey=%s&limit=100&catalog=%s' % (self.BASEURL, self.APIKEY, self.app.mem.catalog)
		req = self.__build_req(url)
		results = self.__get_data_from_rhapsody(req, 10)
		if results:
			return results
		else:
			return False

	def get_top_artists(self):
		print "Rhapapi: getting top artists"
		url = '%sartists/top?apikey=%s&limit=100&catalog=%s' % (self.BASEURL, self.APIKEY, self.app.mem.catalog)
		req = self.__build_req(url)
		results = self.__get_data_from_rhapsody(req, 10)
		if results:
			return results
		else:
			return False

	def get_top_tracks(self):
		print "Rhapapi: getting top tracks"
		url = '%stracks/top?apikey=%s&limit=100&catalog=%s' % (self.BASEURL, self.APIKEY, self.app.mem.catalog)
		req = self.__build_req(url)
		results = self.__get_data_from_rhapsody(req, 10)
		#container = []
		if results:
			#d = {'id': 'playlist', 'tracks': results2}
			#container.append(d)
			#return container
			#utils.prettyprint(results)
			return results
		else:
			return False

	def get_genres(self):
		print "Rhapapi: getting genre tree"
		url = "%sgenres?apikey=%s&catalog=%s" % (self.BASEURL, self.APIKEY, self.app.mem.catalog)
		req = self.__build_req(url)
		results = self.__get_data_from_rhapsody(req, 10)
		if results:
			return results
		else:
			return False

	def get_genre_detail(self, g_id):
		print "Rhapapi: getting genre detail"
		url = "%sgenres/%s?apikey=%s&catalog=%s" % (self.BASEURL, g_id, self.APIKEY, self.app.mem.catalog)
		req = self.__build_req(url)
		results = self.__get_data_from_rhapsody(req, 10)
		if results:
			return results
		else:
			return False


	def get_bio(self, art_id):
		print "Rhapapi: getting artist bio"
		url = "%sartists/%s/bio?apikey=%s&catalog=%s" % (self.BASEURL, art_id, self.APIKEY, self.app.mem.catalog)
		req = self.__build_req(url)
		results = self.__get_data_from_rhapsody(req, 10)
		if results:
			return utils.remove_html_markup(results['bio'])
		else:
			return False

	def get_search_results(self, text, stype):
		print "Rhapapi: getting search results"
		url = "%ssearch?apikey=%s&limit=50&q=%s&type=%s&catalog=%s" % (self.BASEURL, self.APIKEY, urllib.quote_plus(text), stype, self.app.mem.catalog)
		#url = "%ssearch?apikey=%s&q=%s&type=%s" % (self.BASEURL, self.APIKEY, urllib.quote_plus(text), stype)
		req = self.__build_req(url)
		results = self.__get_data_from_rhapsody(req, 10)
		if results:
			return results
		else:
			return False





