import xbmcgui
import xbmc
import xbmcvfs

class DialogBase(xbmcgui.WindowXMLDialog):
    def __init__(self, xmlName, thescriptPath, defaultname, forceFallback):
        #print "I'm the Dialog base dialog class"
        pass


class WinBase(xbmcgui.WindowXML):
    def __init__(self, xmlName, thescriptPath, defaultname, forceFallback):
        #print "I'm the MainWin base dialog class"
        pass