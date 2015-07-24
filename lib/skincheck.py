import xbmc
import xbmcgui
import xbmcvfs
import xbmcaddon
import sys
import os
import shutil




def getPlatform():
    
    if 'win32' in sys.platform:
        p = 'win32'
        print "Windows operating system detected"
    elif 'linux' in sys.platform:
        p = 'linux'
        print "Linux operating system detected"
    elif 'darwin' in sys.platform:
        # gotta be a better way to detect ipad/iphone/atv2
        if 'USER' in os.environ and os.environ['USER'] in ('mobile','frontrow',):
            p = 'ios'
        else: 
            p = 'mac'
            print "MacOS operating system detected"
    else:
        log.error('ERROR: Platform check did not match win32, linux, darwin, or iOS. Was %s instead' % sys.platform)
        p = 'linux'
    return p


def skinfix():
	
	
	if xbmc.getSkinDir() == "skin.confluence":
		sk = xbmcaddon.Addon(id="skin.confluence")
		skinpath = sk.getAddonInfo("path")
		#print "skin path: "+skinpath
		platform = getPlatform()
		print "platform: "+platform

		if platform == 'win32' and "Program" in skinpath:
			print "Non-writeable confluence skin in use. Need to make a copy in userdata folder so we can install fonts."
			dialog = xbmcgui.Dialog()
			if dialog.yesno("Install Fonts?", "Rhapsody needs to restart XBMC and install fonts to proceed. Is this okay?"):
				dest = xbmc.translatePath("special://home/")
				dest2 = os.path.join(dest, 'addons', 'skin.confluence')
				dest3 = dest2 + "\\"   #add trailing backslash to windows paths for xbmcvfs
				print "checking for obsolete confluence copy at "+dest3
				if xbmcvfs.exists(dest3):
					print "Found old writeable confluence skin. Attempting to delete"
					delete_directory(dest3)

					#try:
					#	success = xbmcvfs.rmdir(dest3) #folder must be empty for this rmdir to work
					#while success != 1:
					#	xbmc.sleep(1000)
					#	success = xbmcvfs.rmdir(dest3)
					#	print "Trying to delete the folder....."
					
					#print "success = "+str(success)
					#if not success:
					#	print "dest3 didn't work. trying to delete with dest2 path"
					#	
					#	success = shutil.rmtree(dest2)
					#if success:
					#	print "Folder deleted!"
					#else: 
					#	print "Deleting the folder failed. :-("
					#	dialog.ok("Oh noes!!", "Kodi can't delete the folder. Please manually delete the skin.confluence folder found at "+dest2+" and then relaunch Kodi")
					#	xbmc.executebuiltin( "XBMC.RestartApp()" )
					#	exit()
				print "making a writeable confluence copy"
				shutil.copytree(skinpath, dest2)
				print "Finished copy. retarting app"
				xbmc.executebuiltin( "XBMC.RestartApp()" )
				exit()
			else:
				print 'Font install declined. Aborting Rhapsody launch'
				exit()

		elif platform == 'linux' and "share" in skinpath:
			print "Non-writeable confluence skin in use. Need to make a copy in the userdata folder so we can install fonts."
			dialog = xbmcgui.Dialog()
			if dialog.yesno("Install Fonts?", "Rhapsody needs to restart XBMC and install fonts to proceed. Is this okay?"):
				dest = xbmc.translatePath("special://home/")
				dest2 = os.path.join(dest, 'addons', 'skin.confluence')
				print "checking for obsolete confluence copy"
				if xbmcvfs.exists(dest2):
					print "deleting obsolete confluence copy"
					shutil.rmtree(dest2)
				print "making a writeable confluence copy"
				shutil.copytree(skinpath, dest2)
				print "Finished copy. retarting app"
				xbmc.executebuiltin( "XBMC.RestartApp()" )
				exit()
			else:
				print 'Font install declined. Aborting Rhapsody launch'
				exit()
			
		else:
			pass
			#print "All is okay. Confluence in use is a writeable copy"

	return

## UTIL FILE MANAGEMENT
def copy_directory(source, destination):
	destination = os.path.join(destination, os.path.basename(source))
	xbmcvfs.mkdirs(destination) # todo error if exists?
	dirs, files = xbmcvfs.listdir(source)
	for f in files:
		src = os.path.join(source, f)
		dest = os.path.join(destination, f)
		xbmcvfs.copy(src, dest)
	for d in dirs:
		d = os.path.join(source, d)
		copy_directory(d, destination)

def delete_directory(source):
	dirs, files = xbmcvfs.listdir(source)
	for d in dirs:
		d = os.path.join(source, d)
		delete_directory(d)
	for f in files:
		f = os.path.join(source, f)
		xbmcvfs.delete(f)
	xbmcvfs.rmdir(source)

def copy_files(source, destination, match):
	# create directories if needed
	xbmcvfs.mkdirs(destination)
	# move files from source to destination if match
	dirs, files = xbmcvfs.listdir(source)
	for f in files:
		if match in f:
			src = os.path.join(source, f)
			dest = os.path.join(destination, f)
			xbmcvfs.copy(src, dest) # todo error

def delete_files(source, match, del_empty=False):
	# delete files from source if match
	dirs, files = xbmcvfs.listdir(source)
	for f in files:
		if match in f:
			f = os.path.join(source, f)
			xbmcvfs.delete(f)
	# delete source directory if empty
	if del_empty and len(xbmcvfs.listdir(source)) == 0:
		xbmcvfs.rmdir(source)
