import xbmcgui
import json
import subprocess

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

def goodbye(app):
		dialog = xbmcgui.Dialog()
		if dialog.yesno("Quit Rhapsody?", "Nobody like a quitter. Nobody. "):
			app.set_var('running',False)
			app.player.stop()
			app.player.playlist.clear()
			#app.cache.save_artist_data()
			#app.cache.save_album_data()
			app.win.close()

def update():
	try:
		#subprocess.check_output(["git", "pull"])
		process = subprocess.Popen(["git", "pull"]),
		stdout = subprocess.PIPE
		output = subprocess.communicate()[0]
		print "performed git pull command. "
	except:
		print "something not right with the git pull command"
	