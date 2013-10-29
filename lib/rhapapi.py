import xbmc
import urllib
import urllib2
import json
import base64
from utils import *



class Api():

	def __init__(self):
		self.BASEURL = "http://api.rhapsody.com/v1/"
		self.S_BASEURL = "https://api.rhapsody.com/v1/"
		self.AUTHURL = "https://api.rhapsody.com/oauth/token"
		self.APIKEY = "22Q1bFiwGxYA2eaG4vVAGsJqi3SQWzmd"
		self.SECRET = "Z1AAYBC1JEtnMJGm"


	def __get_data_from_rhapsody(self, req):
		succeed = 0
		while succeed < 5:
			try:
				response = urllib2.urlopen(req)
				results = json.load(response)
				return results
			except urllib2.HTTPError, e:
				print "------------------  Bad server response ----------------"
				print e.headers
				print e
				xbmc.sleep(1000)
				succeed += 1
		return False


#----------- Secure API calls requiring auth headers ---------

	def __build_member_req(self, url, access_token):
		header = b'Bearer ' + access_token
		req = urllib2.Request(url)
		req.add_header('Authorization', header)
		return req


	def login_member(self, username, password):
		data = urllib.urlencode({'username': username, 'password': password, 'grant_type': 'password'})
		header = b'Basic ' + base64.b64encode(self.APIKEY + b':' + self.SECRET)
		req = urllib2.Request(self.AUTHURL, data)
		req.add_header('Authorization', header)
		results = self.__get_data_from_rhapsody(req)
		if results:
			return results
		else:
			return False


	def get_playable_url(self, track_id, access_token):
		url = "%splay/%s" %(self.S_BASEURL, track_id)
		req = self.__build_member_req(url, access_token)
		results = self.__get_data_from_rhapsody(req)
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


#----------- Normal API calls  ---------

	def get_album_review(self, album_id):
		url = "%salbums/%s/reviews?apikey=%s" % (self.BASEURL, album_id, self.APIKEY)
		results = self.__get_data_from_rhapsody(url)
		if results:
			return remove_html_markup(results[0]["body"])
		else:
			return False

	def get_album_details(self, album_id):
		#url = '%salbums/new?apikey=%s&limit=100' % (self.BASEURL, self.APIKEY)
		url = "http://direct.rhapsody.com/metadata/data/methods/getAlbum.js?developerKey=9H9H9E6G1E4I5E0I&albumId=%s&cobrandId=40134&filterRightsKey=0" % (album_id)
		results = self.__get_data_from_rhapsody(url)
		if results:
			return results
		else:
			return False

	def get_album_images(self, album_id):
		url = "%salbums/%s/images?apikey=%s" %(self.BASEURL, album_id, self.APIKEY)
		results = self.__get_data_from_rhapsody(url)
		if results:
			return results
		else:
			return False


	def get_new_releases(self):
		url = '%salbums/new?apikey=%s&limit=100' % (self.BASEURL, self.APIKEY)
		results = self.__get_data_from_rhapsody(url)
		if results:
			return results
		else:
			return False


	def get_top_albums(self):
		url = '%salbums/top?apikey=%s&limit=100' % (self.BASEURL, self.APIKEY)
		results = self.__get_data_from_rhapsody(url)
		if results:
			return results
		else:
			return False

	def get_top_artists(self):
		url = '%sartists/top?apikey=%s&limit=100' % (self.BASEURL, self.APIKEY)
		results = self.__get_data_from_rhapsody(url)
		if results:
			return results
		else:
			return False

	def get_top_tracks(self):
		url = '%stracks/top?apikey=%s&limit=100' % (self.BASEURL, self.APIKEY)
		results = self.__get_data_from_rhapsody(url)
		if results:
			return results
		else:
			return False

	def get_genres(self):
		url = "%sgenres?apikey=%s" % (self.BASEURL, self.APIKEY)
		results = self.__get_data_from_rhapsody(url)
		if results:
			return results
		else:
			return False

