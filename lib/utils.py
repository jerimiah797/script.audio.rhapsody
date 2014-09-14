import xbmcgui
import xbmc
import xbmcvfs
import json
import commands
import subprocess
import os
import sys
import unicodedata
import time
from datetime import datetime

AGE_STAMP = 1410117986.51

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

def open_url():
	url = "http://www.rhapsody.com/freetrial"
	print "opening web browser at "+url
	if sys.platform=='win32':
	    os.startfile(url)
	elif sys.platform=='darwin':
	    subprocess.Popen(['open', url])
	else:
	    try:
	        subprocess.Popen(['xdg-open', url])
	    except OSError:
	        print 'Please open a browser on: '+url

def goodbye(app, choice):

	def bye(app):
		app.set_var('logged_in', True)
		app.set_var('running',False)
		app.player.stop()
		app.player.playlist.clear()
		#app.cache.save_artist_data()
		#app.cache.save_album_data()
		app.srv.stop()
		try:
			app.logwin.close()
			print "closed logwin"
		except:
			pass
		git_pull()
		#open_url()
		app.win.close()

	if choice == True:
		dialog = xbmcgui.Dialog()
		if dialog.yesno("Quit Rhapsody?", "Pressing 'Yes' will quit the Rhapsody plugin"):
			bye(app)
	else:
		bye(app)

def goodbye_while_logged_out(app):
	dialog = xbmcgui.Dialog()
	if dialog.yesno("Quit Rhapsody?", "Pressing 'Yes' will quit the Rhapsody plugin"):
		app.set_var('logged_in', False)
		app.set_var('running',False)
		app.player.stop()
		app.player.playlist.clear()
		#app.cache.save_artist_data()
		#app.cache.save_album_data()
		#try:
		#	app.logwin.close()
		#	print "closed logwin"
		#except:
		#	print "didn't close logwin"
		git_pull()
		app.win.close()

def housekeeper():
	file_flag = xbmcvfs.exists("special://home/userdata/addon_data/script.audio.rhapsody/.clean_me")
	files = [".albumdb.obj", ".artistdb.obj", ".genres.obj", ".rhapuser.obj"]
	#now = time.time()
	#print "current timestamp, type: %s  %s" % (str(now), type(now))
	if file_flag:
		print "Found the clean_me file! Now let's delete it"
		xbmcvfs.delete("special://home/userdata/addon_data/script.audio.rhapsody/.clean_me")
	else:
		print "No clean-me file. Let's check file dates"
		for item in files:
			f = "special://home/userdata/addon_data/script.audio.rhapsody/"+item
			f_os = xbmc.translatePath(f)
			print "Checking "+f_os
			if xbmcvfs.exists(f):
				modifiedTime = os.path.getmtime(f_os)
				if modifiedTime < AGE_STAMP:
					file_flag = True
					print "%s is too old. Let's do some housekeeping." % (item)
					break
	if file_flag:
		print "Deleting files..."
		for item in files:
			f = "special://home/userdata/addon_data/script.audio.rhapsody/"+item
			f_os = xbmc.translatePath(f)
			print "Deleting "+f_os
			if xbmcvfs.exists(f):
				xbmcvfs.delete(f)
		print "Performed housekeeping"
	else:
		print "No housekeeping necessary"


def eval_unicode(s):
    #sum all the unicode fractions
    u = sum(unicodedata.numeric(i) for i in s if unicodedata.category(i)=="No")
    #eval the regular digits (with optional dot) as a float, or default to 0
    n = float("".join(i for i in s if i.isdigit() or i==".") or 0)
    return n+u

