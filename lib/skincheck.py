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


def verifyConfluence():
	return


def copyConfluence():
	return

def skinfix():
	
	
	if xbmc.getSkinDir() == "skin.confluence":
		sk = xbmcaddon.Addon(id="skin.confluence")
		skinpath = sk.getAddonInfo("path")
		#print "skin path: "+skinpath
		platform = getPlatform()
		#print "platform: "+platform

		if platform == 'win32' and "Program" in skinpath:
			print "Non-writeable confluence skin in use. Need to make a copy in userdata folder so we can install fonts."
			dialog = xbmcgui.Dialog()
			if dialog.yesno("Install Fonts?", "Rhapsody needs to restart XBMC to install fonts. Cool?"):
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
			print "All is okay. Confluence in use is a writeable copy"

	return