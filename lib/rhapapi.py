import xbmc
import urllib2
import json
from utils import *



class Api():

	def __init__(self):
		self.BASEURL = "http://api.rhapsody.com/v1/"
		self.S_BASEURL = "https://api.rhapsody.com/v1/"
		self.AUTHURL = "https://api.rhapsody.com/oauth/token"
		self.APIKEY = "22Q1bFiwGxYA2eaG4vVAGsJqi3SQWzmd"
		self.SECRET = "Z1AAYBC1JEtnMJGm"

	def get_playable_url(self, track_id, access_token):
		url = "%splay/%s" %(self.BASEURL, track_id)
		req = self.__build_member_req(url, access_token)
		results = self.__get_data_from_rhapsody(req)
		if results:
			return results['url']
		else:
			return False

	def get_album_review(self, album_id):
		url = "%salbums/%s/reviews?apikey=%s" % (self.BASEURL, album_id, self.APIKEY)
		results = self.__get_data_from_rhapsody(url)
		if results:
			return remove_html_markup(results[0]["body"])
		else:
			return False


	def __build_member_req(self, url, access_token):
		header = b'Bearer ' + access_token
		req = urllib2.Request(url)
		req.add_header('Authorization', header)
		return req


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