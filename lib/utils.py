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

def goodbye(app):
	dialog = xbmcgui.Dialog()
	if dialog.yesno("Quit Rhapsody?", "Pressing 'Yes' will quit the Rhapsody plugin"):
		app.set_var('logged_in', True)
		app.set_var('running',False)
		app.player.stop()
		app.player.playlist.clear()
		#app.cache.save_artist_data()
		#app.cache.save_album_data()
		try:
			app.logwin.close()
			print "closed logwin"
		except:
			pass
		git_pull()
		#open_url()
		app.win.close()

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



