#import xbmcgui
import xbmc

from main import *

script_path = xbmc.translatePath('special://skin') + "scripts/"


def main():
	win = MainWin("main.xml", script_path, 'Default', '720p')
	win.doModal()
	del win
	print "App has been exited"


main()

