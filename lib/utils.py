import xbmcgui
import xbmc
import json
import commands
import subprocess
import os
import sys

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
	out = out.replace("\n", " ")
	return out

def prettyprint(string):
	print(json.dumps(string, sort_keys=True, indent=4, separators=(',', ': ')))



def git_pull():
	plugin_dir = xbmc.translatePath("special://home/addons/script.audio.rhapsody/")
	pr = subprocess.Popen( "git pull" , cwd = plugin_dir, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
	(out, error) = pr.communicate()
	#print "Error : " + str(error) 
	print "Checking for Rhapsody updates: " + str(out)

def goodbye(app):
	dialog = xbmcgui.Dialog()
	if dialog.yesno("Quit Rhapsody?", "Playback will stop and you will return to XBMC "):
		app.set_var('running',False)
		app.player.stop()
		app.player.playlist.clear()
		#app.cache.save_artist_data()
		#app.cache.save_album_data()
		git_pull()
		app.win.close()