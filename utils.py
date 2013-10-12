import xbmc
import xbmcgui
import sys
import time
import urllib
import urllib2
import re
import json
import os

BASEURL = "http://api.rhapsody.com/v1/"
APIKEY = "22Q1bFiwGxYA2eaG4vVAGsJqi3SQWzmd"
APPROOT = xbmc.translatePath('special://skin')

def GetStringFromUrl(encurl):
	doc = ""
	succeed = 0
	while succeed < 5:
		try:
			f = urllib.urlopen(encurl)
			doc = f.read()
			f.close()
			return str(doc)
		except:
			log("could not get data from %s" % encurl)
			xbmc.sleep(1000)
			succeed += 1
	return ""


def prettyprint(string):
	print(json.dumps(string, sort_keys=True, indent=4, separators=(',', ': ')))


def verify_image_dir():
	img_dir = APPROOT+'/scripts/resources/skins/Default/media/album/'
	if (not os.path.isdir(img_dir)):
		os.mkdir(img_dir)
		print ("Created the missing album image directory at " + img_dir)
	else:
		print "Image directory is present!"
	return img_dir

def remove_html_markup(s):
	tag = False
	quote = False
	out = ""
	for c in s:
		if c == '<' and not quote:
			tag = True
		elif c == '>' and not quote:
			tag = False
		elif (c == '"' or c == "'") and tag:
			quote = not quote
		elif not tag:
			out = out + c
	return out
