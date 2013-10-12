# albumdetail.py

import xbmc
import time
import urllib
import urllib2
import json
import pickle
import base64
from utils import *

BASEURL = "http://api.rhapsody.com/v1/"
AUTHURL = 'https://api.rhapsody.com/oauth/token'
APIKEY = "22Q1bFiwGxYA2eaG4vVAGsJqi3SQWzmd"
SECRET = "Z1AAYBC1JEtnMJGm"
APPROOT = xbmc.translatePath('special://skin')

class Member():
	def __init__(self):
		self.logged_in = False
		self.bad_creds = False
		self.info = []
		self.filename = APPROOT+'/.rhapuser.obj'
		self.picklefile = ''
		self.olddevkey = "5C8F8G9G8B4D0E5J"
		self.cobrandId = "40134"
		self.user_info = {}
		self.username = ""
		self.password = ""
		self.access_token = ""
		self.refresh_token = ""
		self.issued_at = ""
		self.expires_in = ""
		self.guid = ""
		self.account_type = "Not available"
		self.date_created = "Not available"
		self.first_name = ""
		self.last_name = ""
		self.catalog = ""
		self.timestamp = ""


	def has_saved_creds(self):
		print "checking saved creds"
		try:
			self.user_info = pickle.load(open(self.filename, 'rb'))
			print "I see the cred file. Here's the contents:"
			#prettyprint(self.user_info)
			self.username = self.user_info['username']
			self.password = base64.b64decode(self.user_info['password'])
			self.guid = self.user_info['guid']
			self.access_token = self.user_info['access_token']
			self.refresh_token = self.user_info['refresh_token']
			self.issued_at = self.user_info['issued_at']
			self.expires_in = self.user_info['expires_in']
			self.first_name = self.user_info['first_name']
			self.last_name = self.user_info['last_name']
			self.catalog = self.user_info['catalog']
			self.timestamp = self.user_info['timestamp']
		except:
			print "Couldn't read saved user data. Login please"
			return False
		print "current time: "+str(time.time())
		print "creds time: "+str(self.timestamp)
		if time.time() - self.timestamp < self.expires_in:
			print "Saved creds look good. Automatic login successful!"
			self.logged_in = True
			return True
		else:
			print "Saved creds have expired. Generating new ones."
			self.login_member(self.username, self.password)

	def save_user_info(self):
		print "Adding data to user_info object"
		self.user_info['username'] = self.username
		self.user_info['password'] = base64.b64encode(self.password)
		self.user_info['guid'] = self.guid
		self.user_info['access_token'] = self.access_token
		self.user_info['refresh_token'] = self.refresh_token
		self.user_info['issued_at'] = self.issued_at
		self.user_info['expires_in'] = self.expires_in
		self.user_info['first_name'] = self.first_name
		self.user_info['last_name'] = self.last_name
		self.user_info['catalog'] = self.catalog
		self.user_info['timestamp'] = time.time()
		#prettyprint(self.user_info)
		print "Saving picklefile..."
		pickle.dump(self.user_info, open(self.filename, 'wb'))
		print "Picklefile saved!"


	def login_member(self, name, pswd):
		self.username = name
		self.password = pswd
		data = urllib.urlencode({'username': self.username, 'password': self.password, 'grant_type': 'password'})
		header = b'Basic ' + base64.b64encode(APIKEY + b':' + SECRET)
		result = "Bad username/password combination"

		req = urllib2.Request(AUTHURL, data)
		req.add_header('Authorization', header)
		try:
			response = urllib2.urlopen(req)
			if response:
				result = json.load(response)
				self.access_token =     result["access_token"]
				self.catalog =          result["catalog"]
				self.expires_in =       result["expires_in"]
				self.first_name =       result["first_name"]
				self.guid =             result["guid"]
				self.issued_at =        result["issued_at"]
				self.last_name =        result["last_name"]
				self.refresh_token =    result["refresh_token"]
				self.logged_in =        True
				self.save_user_info()

		except urllib2.HTTPError, e:
			print e.headers
			print e
			self.logged_in = False
			self.bad_creds = True
		#prettyprint(result)


class Album():

	def __init__(self):
		self.playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)

	def get_big_image(self, albumid, img_dir):
		results = []
		try:
			#url = "http://direct.rhapsody.com/metadata/data/methods/getImagesForAlbum.js?developerKey=9H9H9E6G1E4I5E0I&albumId=%s&cobrandId=40134" % (albumid)
			url = "%salbums/%s/images?apikey=%s" %(BASEURL, albumid, APIKEY)
			response = urllib2.urlopen(url)
			results = json.load(response)
		except:
			print "Bad server response getting large art info"
		if results:
			#prettyprint(results)
			biggest = 0
			biggest_index = 0
			for y in xrange(0, len(results)):
				s = results[y]["width"]
				if (s > biggest):
					biggest = s
					biggest_index = y
			biggest_image = results[biggest_index]["url"].split('/')[
				(len(results[biggest_index]["url"].split('/'))) - 1]
			img_url = results[biggest_index]["url"]
			img_file = img_dir + biggest_image
			if not os.path.isfile(img_file):
				print ("We need to get this file! Starting download")
				while not os.path.isfile(img_file):
					try:
						urllib.urlretrieve(img_url, img_file)
						print ("Downloaded the file :-)")
					except:
						print "File download failed"
						album_img = "AlbumPlaceholder.png"
						return album_img
			else:
				print ("Already have that file! Moving on...")
			return "album/" + biggest_image
		else:
			return "AlbumPlaceholder.png"


	def get_album_review(self, newreleases, pos):
		results = []
		out = ""
		if newreleases[pos]["review"] == "":
			try:
				#url = "http://direct.rhapsody.com/metadata/data/methods/getAlbumReview.js?developerKey=9H9H9E6G1E4I5E0I&albumId=%s&cobrandId=40134" % (newreleases[pos]["album_id"])
				url = "%salbums/%s/reviews?apikey=%s" % (BASEURL, newreleases[pos]["album_id"], APIKEY)
				response = urllib2.urlopen(url)
				results = json.load(response)
			except:
				print "Review api not returning response"
			if results:
				#prettyprint(results)
				newreleases[pos]["review"] = remove_html_markup(results[0]["body"])
				return out
			else:
				print "No review for this album"
				newreleases[pos]["review"] = ""
				return out
		else:
			print "Already have the review for this album"


	def get_album_details(self, newreleases, pos, gen):
		data = []
		if newreleases[pos]["label"] == "":
			print "Getting genre, tracks and label with API call"
			try:
				url = "http://direct.rhapsody.com/metadata/data/methods/getAlbum.js?developerKey=9H9H9E6G1E4I5E0I&albumId=%s&cobrandId=40134&filterRightsKey=0" % (newreleases[pos]["album_id"])
				#url = "%salbums/%s?apikey=%s" %(BASEURL, newreleases[pos]["album_id"], APIKEY)
				response = urllib2.urlopen(url)
				data = json.load(response)
			except:
				print "Album Detail api not returning response"
			if data:
				#prettyprint(data)
				#orig_date = time.strftime('%B %Y', time.localtime(int(data["originalReleaseDate"]["time"]) / 1000))
				#if newreleases[pos]["album_date"] != orig_date:
					#newreleases[pos]["orig_date"] = orig_date
				newreleases[pos]["label"] = data["label"]
				newreleases[pos]["tracks"] = data["trackMetadatas"]
				newreleases[pos]["style"] = data["primaryStyle"]
				#print "Got label and original date for album"
			#prettyprint(newreleases[pos]["tracks"])
		else:
			print "Already have label info for this album"



	def get_large_art(self, newreleases, pos):
		image_dir = verify_image_dir()
		if os.path.isfile(image_dir + newreleases[pos]["bigthumb"][6:]):
			#print "Using cached image for cover art: " + newreleases[pos]["bigthumb"]
			pass
		else:
			#print "Getting album art with API call"
			file = self.get_big_image(newreleases[pos]["album_id"], image_dir)
			newreleases[pos]["bigthumb"] = file
			#print "Big Thumb: " + newreleases[pos]["bigthumb"]

	def get_newreleases(self, mainwin, member):
		if (len(mainwin.newreleases)) > 2:
			mainwin.clearList()
			for x in range (0, len(mainwin.newreleases)):
				mainwin.addItem(mainwin.newreleases[x]["listitem"])
				try:
					print mainwin.newreleases[x]["album"]
				except:
					print "non-ascii character in album name. :-("
			print "populated the window listcontrol with cached newreleases"
			return
		else:
			mainwin.clearList()
			img_dir = verify_image_dir()
			default_album_img = APPROOT+'/scripts/resources/skins/Default/media/'+"AlbumPlaceholder.png"
			results = ""
			try:
				url = '%salbums/new?apikey=%s&limit=100' % (BASEURL, APIKEY)
				response = urllib2.urlopen(url)
				results = json.load(response)
			except:
				print("Error when fetching Rhapsody data from net")
			count = 0
			if results:
				#print results["albums"][3]
				for item in results:
					img_file = item["images"][0]["url"].split('/')[(len(item["images"][0]["url"].split('/'))) - 1]
					img_path = img_dir + img_file
					if not os.path.isfile(img_path):
						try :
							print ("We need to get album art for " + item["name"] + ". Starting download")
						except:
							print "We need to get album art for a non-ascii album title. Starting download"
						#xbmc.log(msg=mess, level=xbmc.LOGDEBUG)
						try:
							while not os.path.isfile(img_path):
								urllib.urlretrieve(item["images"][0]["url"], img_path)
								print("Downloaded " + img_file)
								album = {'album_id': item["id"],
								         'album': item["name"],
								         'thumb': "album/" + img_file,
								         'album_date': time.strftime('%B %Y', time.localtime(int(item["released"]) / 1000)),
								         'orig_date': "",
								         'label': "",
								         'review': "",
								         'bigthumb': "",
								         'tracks': "",
								         'style': '',
								         'artist': item["artist"]["name"],
								         'list_id': count,
								         'artist_id': item["artist"]["id"],
								         'listitem': xbmcgui.ListItem(item["name"], item["artist"]["name"], '',
								                                      "album/" + img_file)}
						except:
							try:
								print("Album art not available for " + item["name"] + ". Using default album image")
							except:
								print "Album art not available for non-ascii album title. Using default album image"
							album = {'album_id': item["id"],
							         'album': item["name"],
							         'thumb': default_album_img,
							         'album_date': time.strftime('%B %Y', time.localtime(int(item["released"]) / 1000)),
							         'orig_date': "",
							         'label': "",
							         'review': "",
							         'bigthumb': "",
							         'tracks': "",
							         'style': '',
							         'artist': item["artist"]["name"],
							         'list_id': count,
							         'artist_id': item["artist"]["id"],
							         'listitem': xbmcgui.ListItem(item["name"], item["artist"]["name"], '', default_album_img)}
					else:
						#print("Already have album art for " + item["name"] + ". Moving on...")
						album = {'album_id': item["id"],
						         'album': item["name"],
						         'thumb': "album/" + img_file,
						         'album_date': time.strftime('%B %Y', time.localtime(int(item["released"]) / 1000)),
						         'orig_date': "",
						         'label': "",
						         'review': "",
						         'bigthumb': "",
						         'tracks': "",
						         'style': '',
						         'artist': item["artist"]["name"],
						         'list_id': count,
						         'artist_id': item["artist"]["id"],
						         'listitem': xbmcgui.ListItem(item["name"], item["artist"]["name"], '', "album/" + img_file)}
					mainwin.newreleases.append(album)
					#print "Added album to list control"
					mainwin.addItem(album["listitem"])
					count += 1

	def get_topalbums(self, mainwin, member):
		pass

	def get_topartists(self, mainwin, member):
		pass

	def get_toptracks(self, mainwin, member):
		pass

	def get_album_tracklist(self, album_list, pos, albumdialog):

		x = 0
		for item in album_list[pos]["tracks"]:
			newlistitem = xbmcgui.ListItem(path="http://dummyurl.org")
			newlistitem.setInfo('music', { 'tracknumber':   int(album_list[pos]["tracks"][x]["trackIndex"]),
			                               'title':         album_list[pos]["tracks"][x]["name"],
			                               'duration':      int(album_list[pos]["tracks"][x]["playbackSeconds"])
			                               })
			albumdialog.addItem(newlistitem)
			x += 1
		print "Added "+str(x)+"tracks to list"

	def get_album_playlist(self, album_list, pos, albumdialog):

		self.playlist.clear()
		x = 0
		for item in album_list[pos]["tracks"]:
			self.playlist.add(album_list[pos]["tracks"][x]["previewURL"], listitem=xbmcgui.ListItem(''))
			x += 1
		print "Added "+str(x)+"tracks to playlist for "+album_list[pos]["album_id"]
		albumdialog.current_playlist_albumId = album_list[pos]["album_id"]





class Genres():
	def __init__(self):
		self.genre_tree = []
		self.genre_dict = {}
		self.get_genre_tree()
		self.flatten_genre_keys(self.genre_tree)
		#print "Genre 458 is : "+self.genre_dict['g.458']


	def get_genre_tree(self):
		results = None
		try:
			url = "%sgenres?apikey=%s" % (BASEURL, APIKEY)
			response = urllib2.urlopen(url)
			results = json.load(response)
		except:
			print "Genres api not returning response"

		if results:
			self.genre_tree = results
		else:
			print "Couldn't retrieve genres!"

	def flatten_genre_keys(self, j):
		for item in j:
			self.genre_dict[item['id']] = item['name']
			#print "added a key for "+item['name']
			if 'subgenres' in item:
				#print "found subgenres. Calling self recursively"
				self.flatten_genre_keys(item['subgenres'])



